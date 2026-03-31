---
title: "How to Reduce Kubernetes Cluster Costs: A Practical Guide"
date: "2026-03-31"
type: "how-to"
description: "Learn proven strategies to cut Kubernetes cluster costs by 30-60% through right-sizing, autoscaling, spot instances, resource quotas, and cost monitoring with Kubecost."
keywords: "how to reduce kubernetes cluster costs, kubernetes cost optimization, kubernetes autoscaling, kubernetes spot instances, kubecost"
---

<div class="tldr">

**TL;DR:** Most Kubernetes clusters waste 50-70% of provisioned resources. You can dramatically reduce costs by right-sizing workloads based on actual usage, implementing HPA/VPA/Karpenter autoscaling, leveraging spot instances for fault-tolerant workloads, enforcing resource quotas per namespace, and monitoring spend with Kubecost. This guide walks through each strategy with concrete kubectl commands and configuration examples.

</div>

## Why Kubernetes Costs Spiral Out of Control

According to the CNCF's 2025 FinOps survey, organizations running Kubernetes overspend by an average of 55%. The root causes are predictable: developers request far more CPU and memory than workloads actually need, clusters stay sized for peak traffic around the clock, and nobody has visibility into what each team is actually spending.

The good news is that most of these problems are solvable with the right configuration. In production environments, the strategies outlined here routinely deliver 30-60% cost reductions without sacrificing reliability.

## Step 1: Right-Size Your Workloads

The single highest-impact change you can make is adjusting resource requests and limits to match actual usage. Start by identifying the gap between what is requested and what is consumed.

### Audit Current Resource Usage

Use `kubectl top` to get a snapshot of actual CPU and memory consumption across your pods:

```bash
kubectl top pods --all-namespaces --sort-by=cpu
```

For a more detailed view, query the metrics server directly to compare requests versus actual usage:

```bash
kubectl get pods --all-namespaces -o custom-columns=\
  NAMESPACE:.metadata.namespace,\
  NAME:.metadata.name,\
  CPU_REQ:.spec.containers[0].resources.requests.cpu,\
  CPU_LIM:.spec.containers[0].resources.limits.cpu,\
  MEM_REQ:.spec.containers[0].resources.requests.memory,\
  MEM_LIM:.spec.containers[0].resources.limits.memory
```

### Identify Over-Provisioned Pods

Look for pods where actual usage is consistently below 20% of the requested resources. A common pattern is a service requesting 1 CPU core but averaging 80m (8%) utilization. That pod is holding 920m of CPU capacity hostage.

For a cluster-wide view, tools like `kubectl-resource-report` generate HTML reports showing utilization ratios:

```bash
# Install the resource report tool
kubectl krew install resource-capacity

# View cluster-wide resource allocation vs capacity
kubectl resource-capacity --sort cpu.request --util
```

### Set Realistic Requests and Limits

Based on your audit, update deployment manifests. A reasonable starting point is setting requests to the P95 of observed usage and limits to 2x the request:

```yaml
resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

Avoid setting CPU limits too aggressively. CPU throttling can cause latency spikes that are difficult to diagnose. Some teams omit CPU limits entirely and rely only on requests for scheduling, while keeping memory limits strict to prevent OOM kills.

## Step 2: Implement Autoscaling at Every Layer

Kubernetes offers autoscaling at the pod level (HPA and VPA) and the node level (Cluster Autoscaler or Karpenter). Combining all three creates a system that scales efficiently in both directions.

### Horizontal Pod Autoscaler (HPA)

HPA adjusts the number of pod replicas based on observed metrics. Configure it for CPU, memory, or custom metrics:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

The `scaleDown` behavior configuration is critical. Without it, HPA can scale down too aggressively during brief traffic dips, causing instability. A 5-minute stabilization window with a 10% step-down prevents thrashing.

### Vertical Pod Autoscaler (VPA)

VPA automatically adjusts resource requests based on historical usage. Install it and create a VPA object:

```bash
# Install VPA
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: "50m"
        memory: "64Mi"
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
```

Important caveat: do not run HPA and VPA on the same metric (e.g., both scaling on CPU). They will conflict. A common pattern is to use HPA for CPU-based horizontal scaling and VPA for memory right-sizing.

### Karpenter for Node-Level Autoscaling

Karpenter has largely replaced the legacy Cluster Autoscaler for AWS-based clusters. It provisions nodes faster and makes better instance type selections:

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general-purpose
spec:
  template:
    spec:
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["on-demand", "spot"]
      - key: node.kubernetes.io/instance-type
        operator: In
        values: ["m6i.large", "m6i.xlarge", "m6a.large", "m6a.xlarge",
                 "m7i.large", "m7i.xlarge"]
      - key: topology.kubernetes.io/zone
        operator: In
        values: ["us-east-1a", "us-east-1b", "us-east-1c"]
  limits:
    cpu: "200"
    memory: "400Gi"
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

The `consolidationPolicy: WhenEmptyOrUnderutilized` setting is what drives real savings. Karpenter will actively bin-pack pods onto fewer nodes and terminate underutilized instances.

## Step 3: Use Spot Instances Strategically

Spot instances cost 60-90% less than on-demand pricing. The tradeoff is that your cloud provider can reclaim them with short notice (2 minutes on AWS). This is acceptable for stateless, fault-tolerant workloads.

### Good Candidates for Spot

- Stateless API servers behind load balancers (with sufficient replicas)
- Batch processing and data pipeline jobs
- CI/CD build agents
- Development and staging environments

### Poor Candidates for Spot

- Databases and stateful services
- Single-replica critical services
- Long-running jobs that cannot checkpoint

### Implementing Spot with Node Affinity

Use node labels and pod affinity rules to control placement:

```yaml
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 80
      preference:
        matchExpressions:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["m6i.large", "m6a.large", "m7i.large"]
```

Diversify across at least 5-10 instance types and 3 availability zones to minimize interruption rates. AWS data shows that diversified spot pools experience interruptions less than 5% of the time.

## Step 4: Enforce Resource Quotas and Limit Ranges

Without guardrails, a single team can monopolize cluster resources. Resource quotas prevent this at the namespace level.

### Set Namespace Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-alpha-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "100"
```

### Set Default Requests with LimitRange

LimitRange ensures every pod gets a default resource request, even if the developer forgets to specify one:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-alpha
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

Check current quota usage across all namespaces:

```bash
kubectl get resourcequota --all-namespaces -o custom-columns=\
  NAMESPACE:.metadata.namespace,\
  NAME:.metadata.name,\
  CPU_USED:.status.used.requests\\.cpu,\
  CPU_HARD:.status.hard.requests\\.cpu,\
  MEM_USED:.status.used.requests\\.memory,\
  MEM_HARD:.status.hard.requests\\.memory
```

## Step 5: Monitor and Attribute Costs with Kubecost

You cannot optimize what you cannot measure. Kubecost provides real-time cost allocation, broken down by namespace, label, deployment, or team.

### Install Kubecost

```bash
helm repo add kubecost https://kubecost.github.io/cost-analyzer/
helm repo update

helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set kubecostToken="your-token-here"
```

### Query Costs via the API

Kubecost exposes an API for programmatic cost queries, useful for building dashboards or alerting:

```bash
# Get cost allocation by namespace for the last 7 days
curl -s http://localhost:9090/model/allocation \
  -d window=7d \
  -d aggregate=namespace \
  -d accumulate=true | jq '.data[0]'
```

### Set Cost Alerts

Configure Kubecost to alert when a namespace exceeds its budget:

```yaml
# values.yaml for Kubecost helm chart
notifications:
  alertConfigs:
    enabled: true
    alerts:
    - type: budget
      threshold: 1000
      window: 7d
      aggregation: namespace
      filter: 'namespace:"team-alpha"'
      slackWebhookUrl: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Kubecost Savings Recommendations

Kubecost analyzes your cluster and provides actionable savings recommendations. Access them at `http://<kubecost-url>/savings` or via the API:

```bash
curl -s http://localhost:9090/model/savings/requestSizing | jq '.[] | {container, recommended_cpu: .targetCPURequest, current_cpu: .currentCPURequest}'
```

This returns per-container recommendations for right-sizing, which feeds directly back into Step 1.

## Putting It All Together: A Cost Reduction Workflow

Here is a practical sequence for implementing these changes in a production cluster:

1. **Week 1:** Install Kubecost and establish a baseline. Identify the top 10 most expensive workloads.
2. **Week 2:** Deploy VPA in recommendation mode (not auto-update) to gather right-sizing data.
3. **Week 3:** Apply right-sizing changes to the top 10 workloads. Measure the impact.
4. **Week 4:** Configure HPA for stateless services. Migrate non-critical workloads to spot instances.
5. **Week 5:** Implement resource quotas per namespace. Set up cost alerts.
6. **Ongoing:** Review Kubecost reports monthly. Feed VPA recommendations into deployment pipelines.

## Common Pitfalls to Avoid

**Setting CPU limits too low.** CPU throttling introduces tail latency that is invisible to most monitoring. If you see P99 latency spikes with no obvious cause, check for CPU throttling with `kubectl top pods` and `cat /sys/fs/cgroup/cpu/cpu.stat` inside the container.

**Scaling down too fast.** Aggressive scale-down policies cause instability during traffic fluctuations. Always use stabilization windows of at least 5 minutes.

**Ignoring persistent volume costs.** EBS volumes and similar persistent storage are often overlooked. Audit unused PVCs regularly:

```bash
kubectl get pvc --all-namespaces --field-selector status.phase=Bound \
  -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,SIZE:.spec.resources.requests.storage
```

**Running spot instances without Pod Disruption Budgets.** Always configure PDBs to ensure graceful handling of spot interruptions:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
spec:
  minAvailable: "50%"
  selector:
    matchLabels:
      app: api-server
```

## Conclusion

Kubernetes cost optimization is not a one-time project. It requires ongoing measurement, adjustment, and discipline. Start with visibility (Kubecost), then right-size your workloads, implement autoscaling at every layer, and enforce quotas to prevent resource sprawl. The tools and configurations in this guide are battle-tested across clusters of all sizes, from small startups running 10 nodes to enterprises managing thousands. The savings are real and, in most cases, achievable within a few weeks of focused effort.
