import kopf
import subprocess
from pykube import Service, Deployment, Namespace, HTTPClient, KubeConfig, ObjectDoesNotExist


def delete(namespace, names, logger):
    api = HTTPClient(KubeConfig.from_file())
    for name in names:
        deploy = Deployment.objects(api, namespace=namespace).get(name=name)
        deploy.delete()
        logger.info(f'delete Deployment: {str(deploy)}')
        service = Service.objects(api, namespace=namespace).get(name=name)
        service.delete()
        logger.info(f'delete Service:    {str(service)}')


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.namespace')
def namespace(spec, old, new, logger, **kwargs):
    logger.info(f'namespace: {old=}, {new=}')
    api = HTTPClient(KubeConfig.from_file())
    if new:
        obj = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': new,
            }
        }
        Namespace(api, obj).create()
    elif old:
        obj = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': old,
            }
        }
        Namespace(api, obj).delete()


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.pipeline.version')
def pipeline(spec, old, new, logger, **kwargs):
    logger.info(f'pipeline: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/pipeline/releases/download/{new}/release.yaml", shell=True, check=True)
    elif old:
        delete('tekton-pipelines',
               ["tekton-pipelines-controller", "tekton-pipelines-webhook"],
               logger)


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.triggers.version')
def triggers(spec, old, new, logger, **kwargs):
    logger.info(f'triggers: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/triggers/releases/download/{new}/release.yaml", shell=True, check=True)
    elif old:
        delete('tekton-pipelines',
               ["tekton-triggers-controller", "tekton-triggers-webhook"],
               logger)


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.dashboard.version')
def dashboard(spec, old, new, logger, **kwargs):
    logger.info(f'dashboard: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/dashboard/releases/download/{new}/tekton-dashboard-release.yaml -n {spec.get('namespace', 'default')}", shell=True, check=True)
    elif old:
        delete('tekton-pipelines',
               ["tekton-dashboard"],
               logger)


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.kaniko.version')
def dashboard(spec, old, new, logger, **kwargs):
    logger.info(f'kaniko: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/master/task/kaniko/{new}/kaniko.yaml -n {spec.get('namespace', 'default')}", shell=True, check=True)
    elif old:
        subprocess.run(f"kubectl delete task.tekton.dev/kaniko -n {spec.get('namespace', 'default')}", shell=True, check=True)


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.git-clone.version')
def dashboard(spec, old, new, logger, **kwargs):
    logger.info(f'git-clone: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/master/task/git-clone/{new}/git-clone.yaml -n {spec.get('namespace', 'default')}", shell=True, check=True)
    elif old:
        subprocess.run(f"kubectl delete task.tekton.dev/git-clone -n {spec.get('namespace', 'default')}", shell=True, check=True)


@kopf.on.delete('tekton.dev', 'v1beta', 'companions')
def uninstall(spec, logger, **kwargs):
    logger.info('uninstall')
    try:
        delete('tekton-pipelines',
               ["tekton-pipelines-controller", "tekton-pipelines-webhook",
                "tekton-triggers-controller", "tekton-triggers-webhook", "tekton-dashboard"],
               logger)

        subprocess.run(f"kubectl delete task.tekton.dev/kaniko -n {spec.get('namespace', 'default')}", shell=True, check=False)
        subprocess.run(f"kubectl delete task.tekton.dev/git-clone -n {spec.get('namespace', 'default')}", shell=True, check=False)

    except ObjectDoesNotExist:
        pass
