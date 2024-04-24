ML Ops

#### Installing kind for running a local Kubernetes cluster

    ➜  ~ brew install kind
    ==> Downloading https://ghcr.io/v2/homebrew/core/kind/manifests/0.22.0
    ####################################################################################################################################################### 100.0%
    ==> Fetching kind
    ==> Downloading https://ghcr.io/v2/homebrew/core/kind/blobs/sha256:d2480cb3a1cd2ac3130810d5e44eb6015bdb659882fc798e3807cfbb41a0f919
    ####################################################################################################################################################### 100.0%
    ==> Pouring kind--0.22.0.arm64_sonoma.bottle.tar.gz
    ==> Caveats
    zsh completions have been installed to:
    /opt/homebrew/share/zsh/site-functions
    ==> Summary
    🍺  /opt/homebrew/Cellar/kind/0.22.0: 8 files, 8.3MB
    ==> Running `brew cleanup kind`...
    Disable this behaviour by setting HOMEBREW_NO_INSTALL_CLEANUP.
    Hide these hints with HOMEBREW_NO_ENV_HINTS (see `man brew`).

    ➜  ~ kind create cluster
    ERROR: failed to create cluster: failed to list nodes: command "docker ps -a --filter label=io.x-k8s.kind.cluster=kind --format '{{.Names}}'" failed with error: exit status 1
    Command Output: Cannot connect to the Docker daemon at unix:///Users/ankitj/.docker/run/docker.sock. Is the docker daemon running?
    ➜  ~ 


#### Started the docker engine locally on my machine

    ➜  ~ kind create cluster
    Creating cluster "kind" ...
    ✓ Ensuring node image (kindest/node:v1.29.2) 🖼 
    ✓ Preparing nodes 📦  
    ✓ Writing configuration 📜 
    ✓ Starting control-plane 🕹️ 
    ✓ Installing CNI 🔌 
    ✓ Installing StorageClass 💾 
    Set kubectl context to "kind-kind"
    You can now use your cluster with:

    kubectl cluster-info --context kind-kind

    Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂


#### Checking if things look OK

    ➜  ~ kubectl cluster-info --context kind-kind
    Kubernetes control plane is running at https://127.0.0.1:54321
    CoreDNS is running at https://127.0.0.1:54321/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

    To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

#### We now have a Kubernetes local cluster running

#### Install Kubeflow Pipelines

```
➜  ~ export PIPELINE_VERSION=2.1.0
➜  ~ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'vars' is deprecated. Please use 'replacements' instead. [EXPERIMENTAL] Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
namespace/kubeflow created
customresourcedefinition.apiextensions.k8s.io/applications.app.k8s.io created
customresourcedefinition.apiextensions.k8s.io/clusterworkflowtemplates.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/cronworkflows.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/scheduledworkflows.kubeflow.org created
customresourcedefinition.apiextensions.k8s.io/viewers.kubeflow.org created
customresourcedefinition.apiextensions.k8s.io/workfloweventbindings.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/workflows.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/workflowtaskresults.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/workflowtasksets.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/workflowtemplates.argoproj.io created
serviceaccount/kubeflow-pipelines-cache-deployer-sa created
clusterrole.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-clusterrole created
clusterrolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-clusterrolebinding created
➜  ~ kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
customresourcedefinition.apiextensions.k8s.io/applications.app.k8s.io condition met
➜  ~ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesStrategicMerge' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'vars' is deprecated. Please use 'replacements' instead. [EXPERIMENTAL] Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesJson6902' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesStrategicMerge' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
I0423 11:20:54.028314   73182 log.go:245] well-defined vars that were never replaced: kfp-app-name,kfp-app-version
serviceaccount/argo created
serviceaccount/kubeflow-pipelines-cache created
serviceaccount/kubeflow-pipelines-container-builder created
serviceaccount/kubeflow-pipelines-metadata-writer created
serviceaccount/kubeflow-pipelines-viewer created
serviceaccount/metadata-grpc-server created
serviceaccount/ml-pipeline created
serviceaccount/ml-pipeline-persistenceagent created
serviceaccount/ml-pipeline-scheduledworkflow created
serviceaccount/ml-pipeline-ui created
serviceaccount/ml-pipeline-viewer-crd-service-account created
serviceaccount/ml-pipeline-visualizationserver created
serviceaccount/mysql created
serviceaccount/pipeline-runner created
role.rbac.authorization.k8s.io/argo-role created
role.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-role created
role.rbac.authorization.k8s.io/kubeflow-pipelines-cache-role created
role.rbac.authorization.k8s.io/kubeflow-pipelines-metadata-writer-role created
role.rbac.authorization.k8s.io/ml-pipeline created
role.rbac.authorization.k8s.io/ml-pipeline-persistenceagent-role created
role.rbac.authorization.k8s.io/ml-pipeline-scheduledworkflow-role created
role.rbac.authorization.k8s.io/ml-pipeline-ui created
role.rbac.authorization.k8s.io/ml-pipeline-viewer-controller-role created
role.rbac.authorization.k8s.io/pipeline-runner created
rolebinding.rbac.authorization.k8s.io/argo-binding created
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-cache-binding created
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-rolebinding created
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-metadata-writer-binding created
rolebinding.rbac.authorization.k8s.io/ml-pipeline created
rolebinding.rbac.authorization.k8s.io/ml-pipeline-persistenceagent-binding created
rolebinding.rbac.authorization.k8s.io/ml-pipeline-scheduledworkflow-binding created
rolebinding.rbac.authorization.k8s.io/ml-pipeline-ui created
rolebinding.rbac.authorization.k8s.io/ml-pipeline-viewer-crd-binding created
rolebinding.rbac.authorization.k8s.io/pipeline-runner-binding created
configmap/kfp-launcher created
configmap/metadata-grpc-configmap created
configmap/ml-pipeline-ui-configmap created
configmap/pipeline-install-config created
configmap/workflow-controller-configmap created
secret/mlpipeline-minio-artifact created
secret/mysql-secret created
service/cache-server created
service/metadata-envoy-service created
service/metadata-grpc-service created
service/minio-service created
service/ml-pipeline created
service/ml-pipeline-ui created
service/ml-pipeline-visualizationserver created
service/mysql created
service/workflow-controller-metrics created
priorityclass.scheduling.k8s.io/workflow-controller created
persistentvolumeclaim/minio-pvc created
persistentvolumeclaim/mysql-pv-claim created
deployment.apps/cache-deployer-deployment created
deployment.apps/cache-server created
deployment.apps/metadata-envoy-deployment created
deployment.apps/metadata-grpc-deployment created
deployment.apps/metadata-writer created
deployment.apps/minio created
deployment.apps/ml-pipeline created
deployment.apps/ml-pipeline-persistenceagent created
deployment.apps/ml-pipeline-scheduledworkflow created
deployment.apps/ml-pipeline-ui created
deployment.apps/ml-pipeline-viewer-crd created
deployment.apps/ml-pipeline-visualizationserver created
deployment.apps/mysql created
deployment.apps/workflow-controller created
```

#### Installing Lens to check Kubernetes cluster via a GUI

#### Checking the progress  of Kubeflow  installation

```
➜  ~ kubectl get pods -n kubeflow --watch
NAME                                               READY   STATUS              RESTARTS   AGE
cache-deployer-deployment-6d8f5b64cd-qpgst         1/1     Running             0          11m
cache-server-7c886f8946-c8mhz                      0/1     ContainerCreating   0          11m
metadata-envoy-deployment-7664786b9c-6zglp         1/1     Running             0          11m
metadata-grpc-deployment-d94cc8676-ndn6d           0/1     Running             0          11m
metadata-writer-5976fcf84b-w57dl                   0/1     ContainerCreating   0          11m
minio-5dc6ff5b96-fntdz                             0/1     ContainerCreating   0          11m
ml-pipeline-768fffd768-j52p9                       0/1     ContainerCreating   0          11m
ml-pipeline-persistenceagent-877d46f9-r57pg        0/1     ContainerCreating   0          11m
ml-pipeline-scheduledworkflow-759bd5bc97-vb887     0/1     ContainerCreating   0          11m
ml-pipeline-ui-85d54689b9-jglmb                    0/1     ContainerCreating   0          11m
ml-pipeline-viewer-crd-66df6f554d-h4hc4            0/1     ContainerCreating   0          11m
ml-pipeline-visualizationserver-67585f8cc4-5dz6q   0/1     ContainerCreating   0          11m
mysql-5b446b5744-fz6jt                             0/1     ContainerCreating   0          11m
workflow-controller-5f4bcf74b5-hvdt9               0/1     ContainerCreating   0          11m
```

##### It was just a waiting game but it took at least 30 mins to get going. Next time it would better suited to allocate more resources to kind docker image 

```
➜  ~ kubectl get pods -n kubeflow
NAME                                               READY   STATUS    RESTARTS         AGE
cache-deployer-deployment-6d8f5b64cd-qpgst         1/1     Running   0                36m
cache-server-7c886f8946-c8mhz                      1/1     Running   0                36m
metadata-envoy-deployment-7664786b9c-6zglp         1/1     Running   0                36m
metadata-grpc-deployment-d94cc8676-ndn6d           1/1     Running   10 (8m42s ago)   36m
metadata-writer-5976fcf84b-w57dl                   1/1     Running   5 (6m45s ago)    36m
minio-5dc6ff5b96-fntdz                             1/1     Running   0                36m
ml-pipeline-768fffd768-j52p9                       1/1     Running   8 (7m46s ago)    36m
ml-pipeline-persistenceagent-877d46f9-r57pg        1/1     Running   6 (4m58s ago)    36m
ml-pipeline-scheduledworkflow-759bd5bc97-vb887     1/1     Running   0                36m
ml-pipeline-ui-85d54689b9-jglmb                    1/1     Running   0                36m
ml-pipeline-viewer-crd-66df6f554d-h4hc4            1/1     Running   0                36m
ml-pipeline-visualizationserver-67585f8cc4-5dz6q   1/1     Running   0                36m
mysql-5b446b5744-fz6jt                             1/1     Running   0                36m
workflow-controller-5f4bcf74b5-hvdt9               1/1     Running   0                36m
```

#### It may not be available in some environments but It’s quite valuable to manage clusters

￼![alt text](<images/Lens.png>)

####  Doing port forwarding to access Kubeflow UI

```
➜  ~ kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
Forwarding from 127.0.0.1:8080 -> 3000
Forwarding from [::1]:8080 -> 3000
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
```

#### We’re in Kubeflow

![alt text](<images/KubeflowDashboard.png>)￼

#### Let’s try a sample pipeline to check if things are working 

I saw some errors with Metadata database MLMD 

Cannot find context with {"typeName":"system.PipelineRun","contextName":"379dc629-17c4-4c1f-947f-572a8af40eb7"}: Cannot find specified context

But it went away after pods retries

#### Tried gain 

Got another error  
unable to start container process: exec: "/var/run/argo/argoexec": stat /var/run/argo/argoexec: no such file or directory: unknown

Found a resolution here 
https://github.com/kubeflow/pipelines/issues/9119

Seems like unstable version of flow executor 

Changed the flow executor

```
➜  ~ export PIPELINE_VERSION=2.1.0
➜  ~ kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-emissary?ref=$PIPELINE_VERSION"
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesStrategicMerge' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'vars' is deprecated. Please use 'replacements' instead. [EXPERIMENTAL] Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesJson6902' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'bases' is deprecated. Please use 'resources' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
# Warning: 'patchesStrategicMerge' is deprecated. Please use 'patches' instead. Run 'kustomize edit fix' to update your Kustomization automatically.
I0423 15:24:21.638379   15847 log.go:245] well-defined vars that were never replaced: kfp-app-version,kfp-app-name
serviceaccount/argo unchanged
serviceaccount/kubeflow-pipelines-cache unchanged
serviceaccount/kubeflow-pipelines-container-builder unchanged
serviceaccount/kubeflow-pipelines-metadata-writer unchanged
serviceaccount/kubeflow-pipelines-viewer unchanged
serviceaccount/metadata-grpc-server unchanged
serviceaccount/ml-pipeline unchanged
serviceaccount/ml-pipeline-persistenceagent unchanged
serviceaccount/ml-pipeline-scheduledworkflow unchanged
serviceaccount/ml-pipeline-ui unchanged
serviceaccount/ml-pipeline-viewer-crd-service-account unchanged
serviceaccount/ml-pipeline-visualizationserver unchanged
serviceaccount/mysql unchanged
serviceaccount/pipeline-runner unchanged
role.rbac.authorization.k8s.io/argo-role unchanged
role.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-role unchanged
role.rbac.authorization.k8s.io/kubeflow-pipelines-cache-role unchanged
role.rbac.authorization.k8s.io/kubeflow-pipelines-metadata-writer-role unchanged
role.rbac.authorization.k8s.io/ml-pipeline unchanged
role.rbac.authorization.k8s.io/ml-pipeline-persistenceagent-role unchanged
role.rbac.authorization.k8s.io/ml-pipeline-scheduledworkflow-role unchanged
role.rbac.authorization.k8s.io/ml-pipeline-ui unchanged
role.rbac.authorization.k8s.io/ml-pipeline-viewer-controller-role unchanged
role.rbac.authorization.k8s.io/pipeline-runner unchanged
rolebinding.rbac.authorization.k8s.io/argo-binding unchanged
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-cache-binding unchanged
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-cache-deployer-rolebinding unchanged
rolebinding.rbac.authorization.k8s.io/kubeflow-pipelines-metadata-writer-binding unchanged
rolebinding.rbac.authorization.k8s.io/ml-pipeline unchanged
rolebinding.rbac.authorization.k8s.io/ml-pipeline-persistenceagent-binding unchanged
rolebinding.rbac.authorization.k8s.io/ml-pipeline-scheduledworkflow-binding unchanged
rolebinding.rbac.authorization.k8s.io/ml-pipeline-ui unchanged
rolebinding.rbac.authorization.k8s.io/ml-pipeline-viewer-crd-binding unchanged
rolebinding.rbac.authorization.k8s.io/pipeline-runner-binding unchanged
configmap/kfp-launcher unchanged
configmap/metadata-grpc-configmap unchanged
configmap/ml-pipeline-ui-configmap unchanged
configmap/pipeline-install-config unchanged
configmap/workflow-controller-configmap configured
secret/mlpipeline-minio-artifact configured
secret/mysql-secret configured
service/cache-server unchanged
service/metadata-envoy-service unchanged
service/metadata-grpc-service unchanged
service/minio-service unchanged
service/ml-pipeline unchanged
service/ml-pipeline-ui unchanged
service/ml-pipeline-visualizationserver unchanged
service/mysql unchanged
service/workflow-controller-metrics unchanged
priorityclass.scheduling.k8s.io/workflow-controller unchanged
persistentvolumeclaim/minio-pvc unchanged
persistentvolumeclaim/mysql-pv-claim unchanged
deployment.apps/cache-deployer-deployment unchanged
deployment.apps/cache-server unchanged
deployment.apps/metadata-envoy-deployment unchanged
deployment.apps/metadata-grpc-deployment unchanged
deployment.apps/metadata-writer unchanged
deployment.apps/minio unchanged
deployment.apps/ml-pipeline unchanged
deployment.apps/ml-pipeline-persistenceagent unchanged
deployment.apps/ml-pipeline-scheduledworkflow unchanged
deployment.apps/ml-pipeline-ui unchanged
deployment.apps/ml-pipeline-viewer-crd unchanged
deployment.apps/ml-pipeline-visualizationserver unchanged
deployment.apps/mysql unchanged
deployment.apps/workflow-controller unchanged
➜  ~ 
```

#### Got a successful run on the demo

￼![alt text](<images/SuccessfulKubeflowRun.png>)


