import kopf
import subprocess
from pykube import Deployment, HTTPClient, KubeConfig


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.pipeline.version')
def pipeline(old, new, logger, **kwargs):
    logger.info(f'pipeline: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/pipeline/releases/download/{new}/release.yaml", shell=True, check=True)
        

@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.triggers.version')
def triggers(old, new, logger, **kwargs):
    logger.info(f'triggers: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/triggers/releases/download/{new}/release.yaml", shell=True, check=True)


@kopf.on.field('tekton.dev', 'v1beta', 'companions', field='spec.dashboard.version')
def dashboard(old, new, logger, **kwargs):
    logger.info(f'dashboard: {old=}, {new=}')
    if new:
        subprocess.run(f"kubectl apply -f https://github.com/tektoncd/dashboard/releases/download/{new}/tekton-dashboard-release.yaml", shell=True, check=True)


@kopf.on.delete('tekton.dev', 'v1beta', 'companions')
def uninstall(spec, logger, **kwargs):
    logger.info('uninstall')
    api = HTTPClient(KubeConfig.from_file())
    try:
        deploy = Deployment.objects(api, namespace=spec.get('namespace', 'tekton-pipelines')).get(name="tekton-pipelines-controller")
        logger.info(f'undeploy {str(deploy)}')
        deploy.delete()
    except pykube.exceptions.ObjectDoesNotExist:
        pass

    try:
        deploy = Deployment.objects(api, namespace=spec.get('namespace', 'tekton-pipelines')).get(name="tekton-pipelines-webhook")
        logger.info(f'undeploy {str(deploy)}')
        deploy.delete()
    except pykube.exceptions.ObjectDoesNotExist:
        pass

    try:
        deploy = Deployment.objects(api, namespace=spec.get('namespace', 'tekton-pipelines')).get(name="tekton-triggers-controller")
        logger.info(f'undeploy {str(deploy)}')
        deploy.delete()
    except pykube.exceptions.ObjectDoesNotExist:
        pass

    try:
        deploy = Deployment.objects(api, namespace=spec.get('namespace', 'tekton-pipelines')).get(name="tekton-triggers-webhook")
        logger.info(f'undeploy {str(deploy)}')
        deploy.delete()
    except pykube.exceptions.ObjectDoesNotExist:
        pass

    try:
        deploy = Deployment.objects(api, namespace=spec.get('namespace', 'tekton-pipelines')).get(name="tekton-dashboard")
        logger.info(f'undeploy {str(deploy)}')
        deploy.delete()
    except pykube.exceptions.ObjectDoesNotExist:
        pass
