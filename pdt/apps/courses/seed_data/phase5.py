"""Fase 5, Escala, Resiliência e Defesa Avançada."""
from ._helpers import m, q

PHASE5 = {
    "name": "Fase 5: Escala, Resiliência e Defesa Avançada",
    "description": "Domínios complexos de segurança distribuída.",
    "topics": [
        # =====================================================================
        # 5.1 Introdução ao Kubernetes
        # =====================================================================
        {
            "title": "Introdução ao Kubernetes (K8s)",
            "summary": "Onde os microsserviços costumam morar.",
            "lesson": {
                "intro": (
                    "Kubernetes é o orquestrador padrão da indústria, e com isso vem complexidade. "
                    "Antes de mergulhar em operadores, service mesh ou GitOps, é preciso dominar "
                    "os primitivos: o que é um Pod, como um Deployment difere de um StatefulSet, "
                    "por que um Service existe, como o controle declarativo funciona. Sem essa "
                    "fundação, cada feature nova vira mistério, cada erro vira exorcismo. Este "
                    "tópico te dá o modelo mental sólido para os 9 que vêm a seguir."
                ),
                "body": (
                    "<h3>1. O modelo mental: declarativo + reconciliação</h3>"
                    "<p>K8s não é um conjunto de scripts que você executa em ordem. É um "
                    "<strong>sistema de controle baseado em estado desejado</strong>. Você "
                    "descreve o que quer (ex.: '3 réplicas de um Deployment com a imagem nginx:1.25 "
                    "expostas via Service'), envia esse desejo ao API server, e dezenas de "
                    "<em>controllers</em> trabalham em loop infinito para fazer a realidade "
                    "convergir ao desejado.</p>"
                    "<pre><code># Loop conceitual de qualquer controller K8s\n"
                    "while True:\n"
                    "    desired = api.get_desired_state()  # do etcd\n"
                    "    actual = api.get_actual_state()    # do cluster\n"
                    "    diff = compare(desired, actual)\n"
                    "    if diff:\n"
                    "        apply_changes(diff)            # cria/atualiza/destrói\n"
                    "    sleep(short_interval)</code></pre>"
                    "<p>Isso muda profundamente como você opera. Você não 'manda matar um pod'. "
                    "Você diz 'quero que esse pod não exista' (deletando o objeto) e o controller "
                    "<em>reconcilia</em>. Se o objeto sumir do etcd, mas o pod continuar rodando, "
                    "o kubelet vai matar. Se o objeto existir mas o pod morrer, o controller cria "
                    "outro. Convergência contínua, não comandos pontuais.</p>"

                    "<h3>2. Arquitetura: control plane e workers</h3>"
                    "<p>Cluster K8s tem dois grupos de nós:</p>"
                    "<ul>"
                    "<li><strong>Control plane</strong> (cérebro):"
                    "<ul>"
                    "<li><code>kube-apiserver</code>: única porta de entrada. REST API + watch streams.</li>"
                    "<li><code>etcd</code>: banco key-value distribuído (Raft). Armazena <em>todo</em> "
                    "o estado do cluster.</li>"
                    "<li><code>kube-scheduler</code>: decide em qual node cada pod vai rodar.</li>"
                    "<li><code>kube-controller-manager</code>: roda os controllers built-in "
                    "(Deployment, ReplicaSet, Node, Endpoint, etc.).</li>"
                    "<li><code>cloud-controller-manager</code>: integra com cloud (LoadBalancer, "
                    "volumes, nodes).</li>"
                    "</ul></li>"
                    "<li><strong>Workers</strong> (onde rodam suas cargas):"
                    "<ul>"
                    "<li><code>kubelet</code>: agente em cada node. Recebe especificação de pods, "
                    "fala com container runtime, reporta status.</li>"
                    "<li><code>kube-proxy</code>: programa iptables/ipvs/eBPF para implementar "
                    "Services.</li>"
                    "<li><strong>Container runtime</strong>: containerd, CRI-O. Roda os containers "
                    "de fato (Docker como runtime foi descontinuado em 1.24+).</li>"
                    "</ul></li>"
                    "</ul>"
                    "<p>Em cluster gerenciado (EKS, GKE, AKS), o control plane é responsabilidade "
                    "do provedor. Você só vê os workers e a API. Em produção, raramente vale "
                    "self-host (operação de etcd em alta disponibilidade não é trivial).</p>"

                    "<h3>3. Os primitivos essenciais</h3>"
                    "<p>K8s tem dezenas de objetos. Você precisa dominar estes:</p>"
                    "<ul>"
                    "<li><strong>Pod</strong>: a menor unidade deployable. 1+ containers que "
                    "compartilham rede (mesmo IP, mesma porta) e volumes. Em 99% dos casos é "
                    "1 container. Sidecars (Istio, Vault Agent, log shipper) são exceções "
                    "úteis.</li>"
                    "<li><strong>ReplicaSet</strong>: garante que N pods existam. Você raramente "
                    "cria diretamente, usa Deployment.</li>"
                    "<li><strong>Deployment</strong>: gerencia ReplicaSets para fazer rolling "
                    "updates. <em>Stateless</em>: não há identidade entre pods.</li>"
                    "<li><strong>StatefulSet</strong>: pods com identidade estável "
                    "(<code>app-0</code>, <code>app-1</code>) e armazenamento persistente associado. "
                    "Para DBs, Kafka, Elasticsearch.</li>"
                    "<li><strong>DaemonSet</strong>: 1 pod por node. Para agentes (CNI, log "
                    "collector, node-exporter, Falco).</li>"
                    "<li><strong>Job / CronJob</strong>: batch. Job roda até completar. CronJob "
                    "agenda Jobs com cron syntax.</li>"
                    "<li><strong>Service</strong>: endpoint estável + load balancer L4 para um "
                    "conjunto de pods (selecionados por label). Sem Service, IP dos pods muda "
                    "a cada deploy e não há balanceamento.</li>"
                    "<li><strong>Ingress</strong>: roteamento HTTP/HTTPS externo (host + path). "
                    "Precisa de um <em>ingress-controller</em> (NGINX, Traefik, HAProxy) "
                    "implementando o objeto.</li>"
                    "<li><strong>ConfigMap</strong>: configuração não-sensível (env, arquivos).</li>"
                    "<li><strong>Secret</strong>: configuração sensível (apenas base64 por padrão; "
                    "habilite encryption-at-rest no etcd, ver tópico 5.2).</li>"
                    "<li><strong>Namespace</strong>: agrupamento lógico. <em>Não</em> é boundary "
                    "forte de segurança, apenas escopo de objetos.</li>"
                    "<li><strong>PersistentVolume / PersistentVolumeClaim</strong>: storage "
                    "persistente. PV é o recurso, PVC é o pedido.</li>"
                    "<li><strong>ServiceAccount</strong>: identidade de uma carga (não de um "
                    "humano). Usada para autenticar contra a API.</li>"
                    "</ul>"

                    "<h3>4. Pod: o coração do K8s</h3>"
                    "<pre><code>apiVersion: v1\n"
                    "kind: Pod\n"
                    "metadata:\n"
                    "  name: web\n"
                    "  labels:\n"
                    "    app: web\n"
                    "spec:\n"
                    "  containers:\n"
                    "  - name: nginx\n"
                    "    image: nginx:1.25@sha256:abcdef...\n"
                    "    ports:\n"
                    "    - containerPort: 80\n"
                    "    resources:\n"
                    "      requests:\n"
                    "        cpu: 100m\n"
                    "        memory: 128Mi\n"
                    "      limits:\n"
                    "        cpu: 500m\n"
                    "        memory: 256Mi\n"
                    "    livenessProbe:\n"
                    "      httpGet: { path: /, port: 80 }\n"
                    "      periodSeconds: 10\n"
                    "    readinessProbe:\n"
                    "      httpGet: { path: /healthz, port: 80 }\n"
                    "      periodSeconds: 5\n"
                    "    securityContext:\n"
                    "      runAsNonRoot: true\n"
                    "      runAsUser: 101\n"
                    "      readOnlyRootFilesystem: true\n"
                    "      allowPrivilegeEscalation: false\n"
                    "      capabilities:\n"
                    "        drop: [\"ALL\"]\n"
                    "  securityContext:\n"
                    "    seccompProfile:\n"
                    "      type: RuntimeDefault</code></pre>"
                    "<p>Observe os blocos:</p>"
                    "<ul>"
                    "<li><strong>resources</strong>: <code>requests</code> é o que o scheduler "
                    "usa para decidir node; <code>limits</code> é o teto que o cgroup impõe. Sem "
                    "requests, scheduler chuta; sem limits, pod pode comer node todo.</li>"
                    "<li><strong>livenessProbe</strong>: se falhar, kubelet reinicia o container. "
                    "Use para detectar deadlock, não para healthcheck dependente de DB (cascata "
                    "de restart se DB cair).</li>"
                    "<li><strong>readinessProbe</strong>: se falhar, pod sai do Service "
                    "(Endpoints). Use para 'estou pronto para receber tráfego'. Carga inicial, "
                    "warm-up de cache, etc.</li>"
                    "<li><strong>securityContext</strong>: ver tópico 5.2 (Hardening). "
                    "<code>runAsNonRoot</code>, <code>readOnlyRootFilesystem</code>, drop de "
                    "<code>ALL</code> capabilities é o mínimo aceitável.</li>"
                    "</ul>"

                    "<h3>5. Deployment: o que você usa no dia a dia</h3>"
                    "<pre><code>apiVersion: apps/v1\n"
                    "kind: Deployment\n"
                    "metadata:\n"
                    "  name: web\n"
                    "  namespace: prod\n"
                    "spec:\n"
                    "  replicas: 5\n"
                    "  selector:\n"
                    "    matchLabels: { app: web }\n"
                    "  strategy:\n"
                    "    type: RollingUpdate\n"
                    "    rollingUpdate:\n"
                    "      maxSurge: 25%       # quantos pods extras durante rollout\n"
                    "      maxUnavailable: 0   # zero downtime\n"
                    "  template:\n"
                    "    metadata:\n"
                    "      labels: { app: web }\n"
                    "    spec:\n"
                    "      containers:\n"
                    "      - name: web\n"
                    "        image: ghcr.io/me/web:v1.2.3\n"
                    "        # ... resources, probes, securityContext\n"
                    "      topologySpreadConstraints:\n"
                    "      - maxSkew: 1\n"
                    "        topologyKey: topology.kubernetes.io/zone\n"
                    "        whenUnsatisfiable: ScheduleAnyway\n"
                    "        labelSelector:\n"
                    "          matchLabels: { app: web }</code></pre>"
                    "<p>Conceitos importantes:</p>"
                    "<ul>"
                    "<li><strong>RollingUpdate</strong>: substitui pods aos poucos. "
                    "<code>maxUnavailable: 0</code> + <code>maxSurge: 25%</code> garante zero "
                    "downtime (cria novos antes de matar antigos).</li>"
                    "<li><strong>Recreate</strong>: outra estratégia, mata todos, depois cria. "
                    "Há downtime; útil quando há migration de schema incompatível.</li>"
                    "<li><strong>topologySpreadConstraints</strong>: distribui pods entre AZs. "
                    "Sem isso, scheduler pode colocar tudo numa AZ e você perde tudo se ela cair.</li>"
                    "<li><strong>imagem com tag mutável (<code>:latest</code>, <code>:main</code>)</strong> "
                    "é antipattern: deploy não é reproducível. Use SemVer ou digest "
                    "(<code>@sha256:...</code>).</li>"
                    "</ul>"

                    "<h3>6. Service: endpoint estável</h3>"
                    "<p>Pods são gado, não animais de estimação: criados e destruídos. IPs "
                    "mudam. Como você fala com 'a app web', não com 'o IP 10.0.3.42'?</p>"
                    "<pre><code>apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    "  name: web\n"
                    "spec:\n"
                    "  type: ClusterIP\n"
                    "  selector: { app: web }\n"
                    "  ports:\n"
                    "  - port: 80\n"
                    "    targetPort: 8080</code></pre>"
                    "<p>Tipos de Service:</p>"
                    "<ul>"
                    "<li><strong>ClusterIP</strong> (default): IP virtual interno. Para "
                    "comunicação entre pods. Resolvido por DNS interno: "
                    "<code>web.prod.svc.cluster.local</code>.</li>"
                    "<li><strong>NodePort</strong>: abre uma porta (30000-32767) em todo node. "
                    "Pra dev/teste; em prod use Ingress ou LoadBalancer.</li>"
                    "<li><strong>LoadBalancer</strong>: pede ao cloud um LB externo (AWS NLB, "
                    "GCP LB). Caro se você tem 50 services, combine com Ingress.</li>"
                    "<li><strong>ExternalName</strong>: alias DNS para serviço externo "
                    "(<code>db.prod.svc.cluster.local → rds.amazonaws.com</code>).</li>"
                    "<li><strong>Headless</strong> (<code>clusterIP: None</code>): retorna IPs "
                    "dos pods diretamente. Para StatefulSets e service discovery custom.</li>"
                    "</ul>"

                    "<h3>7. Ingress: HTTP/S externo</h3>"
                    "<p>LoadBalancer por Service é caro. Ingress oferece um único entry-point "
                    "com roteamento por host/path:</p>"
                    "<pre><code>apiVersion: networking.k8s.io/v1\n"
                    "kind: Ingress\n"
                    "metadata:\n"
                    "  name: app\n"
                    "  annotations:\n"
                    "    cert-manager.io/cluster-issuer: letsencrypt\n"
                    "spec:\n"
                    "  ingressClassName: nginx\n"
                    "  tls:\n"
                    "  - hosts: [app.example.com]\n"
                    "    secretName: app-tls\n"
                    "  rules:\n"
                    "  - host: app.example.com\n"
                    "    http:\n"
                    "      paths:\n"
                    "      - path: /api\n"
                    "        pathType: Prefix\n"
                    "        backend:\n"
                    "          service: { name: api, port: { number: 80 } }\n"
                    "      - path: /\n"
                    "        pathType: Prefix\n"
                    "        backend:\n"
                    "          service: { name: web, port: { number: 80 } }</code></pre>"
                    "<p>Você precisa de um <em>ingress controller</em> instalado (NGINX, Traefik, "
                    "HAProxy, GKE Ingress). Ele lê os objetos Ingress e configura o proxy real. "
                    "<strong>Gateway API</strong> (mais novo) é o sucessor de Ingress, com modelo "
                    "mais expressivo.</p>"

                    "<h3>8. Probes: liveness, readiness, startup</h3>"
                    "<p>Sem probes, K8s manda tráfego para pod ainda subindo. Com probes "
                    "ruins, pod entra em loop de restart por motivos errados. Distinguir é "
                    "essencial:</p>"
                    "<ul>"
                    "<li><strong>livenessProbe</strong>: 'estou vivo?'. Falhar = container "
                    "reiniciado. <em>Não</em> dependa de DB externo aqui, você causa "
                    "cascading failure.</li>"
                    "<li><strong>readinessProbe</strong>: 'posso receber tráfego?'. Falhar = "
                    "pod removido do Service mas <em>não</em> reiniciado. Use para "
                    "warm-up, dependency check.</li>"
                    "<li><strong>startupProbe</strong>: 'já terminei de iniciar?'. Roda primeiro; "
                    "enquanto não passa, liveness/readiness não rodam. Para apps com boot "
                    "demorado (Java, .NET).</li>"
                    "</ul>"
                    "<pre><code># Bom\n"
                    "livenessProbe:\n"
                    "  exec: { command: [\"/bin/sh\", \"-c\", \"pgrep -f myapp || exit 1\"] }\n"
                    "  periodSeconds: 30\n"
                    "  failureThreshold: 3\n"
                    "readinessProbe:\n"
                    "  httpGet: { path: /ready, port: 8080 }\n"
                    "  periodSeconds: 5\n"
                    "  failureThreshold: 1\n"
                    "startupProbe:\n"
                    "  httpGet: { path: /healthz, port: 8080 }\n"
                    "  periodSeconds: 10\n"
                    "  failureThreshold: 30  # 5 min para subir</code></pre>"

                    "<h3>9. ConfigMap e Secret</h3>"
                    "<pre><code>apiVersion: v1\n"
                    "kind: ConfigMap\n"
                    "metadata: { name: app-config }\n"
                    "data:\n"
                    "  log_level: info\n"
                    "  api_url: https://api.example.com\n"
                    "---\n"
                    "apiVersion: v1\n"
                    "kind: Secret\n"
                    "metadata: { name: app-secret }\n"
                    "type: Opaque\n"
                    "data:\n"
                    "  db_password: cGFzczEyMw==  # base64</code></pre>"
                    "<p>Injete em pods de duas formas:</p>"
                    "<pre><code>spec:\n"
                    "  containers:\n"
                    "  - name: app\n"
                    "    envFrom:\n"
                    "    - configMapRef: { name: app-config }\n"
                    "    - secretRef: { name: app-secret }\n"
                    "    # ou monte como arquivo\n"
                    "    volumeMounts:\n"
                    "    - name: secret-vol\n"
                    "      mountPath: /etc/secrets\n"
                    "      readOnly: true\n"
                    "  volumes:\n"
                    "  - name: secret-vol\n"
                    "    secret: { secretName: app-secret }</code></pre>"
                    "<p><strong>Cuidado</strong>: Secret é só base64, não criptografia. "
                    "Em produção: External Secrets Operator (puxa do Vault/AWS Secrets Manager) "
                    "ou SealedSecrets (Bitnami) para GitOps. Em todo caso, encryption-at-rest "
                    "do etcd ligado.</p>"

                    "<h3>10. Helm: gerência de releases</h3>"
                    "<p>YAML repetido em 4 ambientes (dev/qa/staging/prod) vira inferno. "
                    "<strong>Helm</strong> empacota manifests em <em>charts</em> com templates "
                    "Go e arquivo de <em>values</em> por ambiente:</p>"
                    "<pre><code>mychart/\n"
                    "├── Chart.yaml\n"
                    "├── values.yaml          # defaults\n"
                    "├── values-prod.yaml     # overrides\n"
                    "└── templates/\n"
                    "    ├── deployment.yaml\n"
                    "    └── service.yaml\n"
                    "\n"
                    "$ helm install myapp ./mychart -f values-prod.yaml --namespace prod\n"
                    "$ helm upgrade myapp ./mychart -f values-prod.yaml --namespace prod\n"
                    "$ helm rollback myapp 1 --namespace prod</code></pre>"
                    "<p>Charts ficam em registry OCI (ECR, GAR, GHCR), versionados como imagem. "
                    "Alternativas: Kustomize (overlays YAML, sem template engine) e operadores "
                    "(controllers customizados que entendem CRDs).</p>"

                    "<h3>11. GitOps: Argo CD e Flux</h3>"
                    "<p>Você ainda corre <code>kubectl apply</code> manualmente? Em produção "
                    "moderna, ninguém faz isso. <strong>GitOps</strong> torna o repo Git a "
                    "fonte da verdade do cluster:</p>"
                    "<ol>"
                    "<li>Engenheiro abre PR alterando manifest no repo.</li>"
                    "<li>PR é revisado, mergeado.</li>"
                    "<li>Argo CD (rodando no cluster) detecta o commit, compara com cluster, "
                    "aplica diff.</li>"
                    "<li>Drift no cluster (alguém mexeu manualmente)? Argo reverte ou alerta.</li>"
                    "</ol>"
                    "<p>Benefícios: trilha de auditoria via Git, rollback é um <code>git revert</code>, "
                    "permissões reduzidas (engenheiros não precisam de kubectl em prod).</p>"

                    "<h3>12. Distribuições e gerenciados</h3>"
                    "<ul>"
                    "<li><strong>kind / minikube</strong>: K8s local para dev e testes.</li>"
                    "<li><strong>k3s / k0s</strong>: K8s leve para edge/IoT/CI.</li>"
                    "<li><strong>kubeadm</strong>: vanilla, você monta. Útil para aprender; "
                    "raro em prod por operação.</li>"
                    "<li><strong>OpenShift, Rancher, Tanzu</strong>: distribuições comerciais "
                    "com features extras.</li>"
                    "<li><strong>EKS, GKE, AKS</strong>: gerenciados (cloud opera control plane).</li>"
                    "</ul>"
                    "<p>Para 95% dos casos, gerenciado. Self-host é justificado por compliance, "
                    "edge ou bare-metal específico.</p>"

                    "<h3>13. Comandos kubectl essenciais</h3>"
                    "<pre><code># Visualizar\n"
                    "kubectl get pods -n prod -o wide\n"
                    "kubectl describe pod web-abc -n prod\n"
                    "kubectl logs -f web-abc -n prod\n"
                    "kubectl logs --previous web-abc -n prod  # após restart\n"
                    "kubectl top pod -n prod                  # CPU/RAM\n"
                    "\n"
                    "# Aplicar/remover\n"
                    "kubectl apply -f manifests/\n"
                    "kubectl delete -f manifests/web.yaml\n"
                    "kubectl scale deploy web --replicas=10 -n prod\n"
                    "\n"
                    "# Debug\n"
                    "kubectl exec -it web-abc -n prod -- /bin/sh\n"
                    "kubectl port-forward svc/web 8080:80 -n prod\n"
                    "kubectl run debug --rm -it --image=busybox -- sh\n"
                    "kubectl debug -it web-abc --image=busybox -n prod  # ephemeral container\n"
                    "\n"
                    "# Diff e dry-run\n"
                    "kubectl diff -f manifest.yaml\n"
                    "kubectl apply -f manifest.yaml --dry-run=server\n"
                    "\n"
                    "# Eventos (chave em troubleshooting)\n"
                    "kubectl get events -n prod --sort-by=.lastTimestamp</code></pre>"

                    "<h3>14. Anti-patterns frequentes</h3>"
                    "<ul>"
                    "<li><strong>Pod sem requests/limits</strong>: scheduler chuta, noisy "
                    "neighbor mata vizinhos.</li>"
                    "<li><strong>livenessProbe que depende de DB externo</strong>: cascading "
                    "failure quando DB hiccup.</li>"
                    "<li><strong>imagem :latest</strong>: deploy não-reproduzível.</li>"
                    "<li><strong>Tudo em namespace <code>default</code></strong>: NetworkPolicy/"
                    "RBAC viram pesadelo.</li>"
                    "<li><strong>Logar em arquivo dentro do pod</strong>: viola 12-factor; "
                    "use stdout.</li>"
                    "<li><strong>HostPath para 'persistência'</strong>: escapa do isolamento; "
                    "use PV.</li>"
                    "<li><strong>1 réplica em prod</strong>: rolling update vira recreate; "
                    "qualquer node maintenance derruba app.</li>"
                    "</ul>"

                    "<h3>15. Quando NÃO usar K8s</h3>"
                    "<p>K8s é ferramenta poderosa mas tem custo operacional alto. <em>Para "
                    "apps simples</em> (1-3 services, baixo tráfego), Docker Compose, ECS, "
                    "Cloud Run ou Fly.io entregam mais valor com menos complexidade. K8s brilha "
                    "quando você tem dezenas+ de microsserviços, autoscaling complexo, "
                    "compliance que exige observability/policy avançado, ou time grande "
                    "trabalhando em paralelo. Não use K8s só porque virou padrão, use porque "
                    "resolve seu problema.</p>"
                ),
                "practical": (
                    "Suba <code>kind create cluster</code> local. Crie um Deployment de NGINX "
                    "com 3 réplicas via <code>kubectl create deploy nginx --image=nginx:1.25 "
                    "--replicas=3</code>. Exponha via <code>kubectl expose deploy nginx --port=80 "
                    "--type=ClusterIP</code>. Use <code>kubectl port-forward svc/nginx 8080:80</code> "
                    "e abra <code>http://localhost:8080</code>. Em seguida, escreva um manifest "
                    "Deployment+Service+ConfigMap em YAML, aplique com <code>kubectl apply</code>, "
                    "e depois remova com <code>kubectl delete -f</code>. Por fim, instale o NGINX "
                    "Ingress Controller via Helm e crie um Ingress roteando <code>app.local</code> "
                    "para o Service."
                ),
            },
            "materials": [
                m("Kubernetes Docs", "https://kubernetes.io/docs/home/", "docs", ""),
                m("Kubernetes the Hard Way", "https://github.com/kelseyhightower/kubernetes-the-hard-way", "course", ""),
                m("kind (local k8s)", "https://kind.sigs.k8s.io/", "tool", ""),
                m("Helm", "https://helm.sh/docs/", "docs", ""),
                m("ArgoCD", "https://argo-cd.readthedocs.io/", "tool", ""),
                m("k8s.io: Tutorials", "https://kubernetes.io/docs/tutorials/", "course", ""),
                m("Kubernetes Patterns (livro)", "https://k8spatterns.io/", "book", ""),
                m("Kubernetes Failure Stories", "https://k8s.af/", "article", "Aprender pelos erros dos outros."),
            ],
            "questions": [
                q("Pod é:",
                  "Menor unidade deployable, com 1+ containers compartilhando rede e volumes.",
                  ["Tipo de Service.", "Cluster inteiro.", "Versão do kubectl."],
                  "Pod tem 1 IP, namespace de rede comum. Containers laterais (sidecar) compartilham."),
                q("Deployment garante:",
                  "Estado desejado de réplicas e rolling update.",
                  ["Apenas 1 pod.", "Substitui Service.", "Apenas em namespace default."],
                  "Cria/gerencia ReplicaSets. Update gradual com max-surge/max-unavailable."),
                q("Service do tipo ClusterIP:",
                  "Expõe internamente ao cluster.",
                  ["Expõe na internet.", "Apenas TCP.", "Apenas IPv6."],
                  "Para externo: NodePort, LoadBalancer ou Ingress (preferido para HTTP)."),
                q("Ingress serve para:",
                  "Roteamento HTTP/S externo.",
                  ["Roteamento de armazenamento.", "Substituir Service.", "Apenas DNS."],
                  "Precisa de ingress-controller (NGINX, Traefik) implementando o objeto Ingress."),
                q("ConfigMap e Secret:",
                  "Injetam configuração e segredos em pods.",
                  ["São o mesmo recurso.", "São storage.", "São métricas."],
                  "Secret é base64, não cripto. Habilite encryption-at-rest no etcd e use externos."),
                q("kubectl apply:",
                  "Aplica manifests declarativos.",
                  ["Apaga cluster.", "Substitui kubelet.", "Cria Helm chart."],
                  "Idempotente. Compara desejado vs atual e ajusta. Use server-side apply em casos avançados."),
                q("Helm chart é:",
                  "Pacote de manifests com templates e values.",
                  ["Alternativa ao kubectl.", "Banco de dados.", "Apenas YAML estático."],
                  "Permite parametrizar releases por ambiente. Subindo charts em registry OCI versiona como imagem."),
                q("Namespace serve para:",
                  "Isolar recursos logicamente no cluster.",
                  ["Substituir VPC.", "Apenas RBAC.", "Substituir IAM."],
                  "Não é boundary forte de segurança, combine com NetworkPolicy + RBAC para isolar."),
                q("Probe (liveness/readiness):",
                  "Indica saúde e prontidão do pod.",
                  ["Apaga pods.", "Aumenta réplica.", "Substitui Service."],
                  "Liveness reinicia container. Readiness controla recebimento de tráfego."),
                q("Argo CD entrega via:",
                  "GitOps, sincroniza estado com Git.",
                  ["Cron.", "FTP.", "Manual."],
                  "Argo monitora repo; aplica diff continuamente. Drift é corrigido automaticamente."),
            ],
        },
        # =====================================================================
        # 5.2 K8s Hardening
        # =====================================================================
        {
            "title": "K8s Hardening",
            "summary": "Blindar o cluster contra invasões.",
            "lesson": {
                "intro": (
                    "K8s default não é seguro, é flexível. Em sua configuração padrão um pod "
                    "pode rodar como root, montar o filesystem do host, abrir socket privilegiado "
                    "e falar com qualquer outro pod do cluster. Hardening é o trabalho de "
                    "transformar essa flexibilidade em postura defensável. As referências "
                    "obrigatórias são CIS Kubernetes Benchmark e NSA/CISA Kubernetes Hardening "
                    "Guidance, leia ambos pelo menos uma vez. Este tópico cobre os controles "
                    "mais impactantes."
                ),
                "body": (
                    "<h3>1. Modelo de ameaças do cluster</h3>"
                    "<p>Antes de aplicar checklist, entenda contra o quê está se defendendo:</p>"
                    "<ul>"
                    "<li><strong>Atacante externo</strong>: explora aplicação web, escala para "
                    "container, escala para node, escala para cluster.</li>"
                    "<li><strong>Insider</strong>: dev com kubectl tenta acessar ns que não "
                    "deveria; CI com token amplo demais.</li>"
                    "<li><strong>Container breakout</strong>: exploração de runtime ou kernel "
                    "para escapar do isolamento.</li>"
                    "<li><strong>Supply chain</strong>: imagem maliciosa puxada de registry "
                    "público.</li>"
                    "<li><strong>Misconfig</strong>: a maior fonte de incidentes, Secret "
                    "exposto, RBAC permissivo, sem encryption.</li>"
                    "</ul>"
                    "<p>Hardening combate todos. Defesa em camadas: nenhum controle resolve sozinho.</p>"

                    "<h3>2. RBAC granular</h3>"
                    "<p>RBAC controla quem pode fazer o quê na API. Quatro objetos:</p>"
                    "<ul>"
                    "<li><strong>Role</strong>: permissões em um namespace.</li>"
                    "<li><strong>ClusterRole</strong>: permissões cluster-wide ou em recursos "
                    "não-namespaced (Node, PV).</li>"
                    "<li><strong>RoleBinding</strong>: amarra Role a usuário/grupo/SA.</li>"
                    "<li><strong>ClusterRoleBinding</strong>: amarra ClusterRole.</li>"
                    "</ul>"
                    "<pre><code>apiVersion: rbac.authorization.k8s.io/v1\n"
                    "kind: Role\n"
                    "metadata:\n"
                    "  namespace: app\n"
                    "  name: pod-reader\n"
                    "rules:\n"
                    "- apiGroups: [\"\"]\n"
                    "  resources: [\"pods\", \"pods/log\"]\n"
                    "  verbs: [\"get\", \"list\"]\n"
                    "---\n"
                    "apiVersion: rbac.authorization.k8s.io/v1\n"
                    "kind: RoleBinding\n"
                    "metadata:\n"
                    "  name: alice-pod-reader\n"
                    "  namespace: app\n"
                    "subjects:\n"
                    "- kind: User\n"
                    "  name: alice@example.com\n"
                    "roleRef:\n"
                    "  kind: Role\n"
                    "  name: pod-reader\n"
                    "  apiGroup: rbac.authorization.k8s.io</code></pre>"
                    "<p>Princípios:</p>"
                    "<ul>"
                    "<li>Comece com <code>cluster-admin</code> apenas para break-glass + MFA.</li>"
                    "<li>Para apps, conceda <em>menos do que parece necessário</em> e adicione "
                    "conforme erros surgem.</li>"
                    "<li>Audite com <code>kubectl auth can-i --list "
                    "--as=system:serviceaccount:ns:sa</code>.</li>"
                    "<li>Verbos <code>create</code>/<code>delete</code>/<code>impersonate</code>"
                    " são especialmente sensíveis. <code>impersonate</code> pode burlar todo o RBAC.</li>"
                    "<li>Controlar verbos não basta: quem cria Role com poderes amplos pode "
                    "elevar privilégio. Separe quem administra RBAC de quem usa.</li>"
                    "</ul>"

                    "<h3>3. Pod Security Standards (PSS)</h3>"
                    "<p>PodSecurityPolicy (PSP) foi removido. O substituto é PSS, três níveis "
                    "aplicáveis por namespace via labels:</p>"
                    "<ul>"
                    "<li><strong>privileged</strong>: sem restrições. Para infra de cluster.</li>"
                    "<li><strong>baseline</strong>: bloqueia o óbvio (privileged, hostPID, "
                    "hostNetwork, hostPath, etc.). Dev pode usar.</li>"
                    "<li><strong>restricted</strong>: estado da arte. Exige runAsNonRoot, "
                    "drop ALL capabilities, seccompProfile, readOnlyRootFilesystem etc. Use em prod.</li>"
                    "</ul>"
                    "<pre><code>kubectl label ns prod \\\n"
                    "  pod-security.kubernetes.io/enforce=restricted \\\n"
                    "  pod-security.kubernetes.io/enforce-version=latest \\\n"
                    "  pod-security.kubernetes.io/warn=restricted \\\n"
                    "  pod-security.kubernetes.io/audit=restricted</code></pre>"
                    "<p>Três modos:</p>"
                    "<ul>"
                    "<li><code>enforce</code>: bloqueia.</li>"
                    "<li><code>warn</code>: avisa em <code>kubectl apply</code>.</li>"
                    "<li><code>audit</code>: log no audit-log.</li>"
                    "</ul>"
                    "<p>Para granularidade além disso: Kyverno, OPA Gatekeeper (ver tópico 5.4).</p>"

                    "<h3>4. securityContext: o mínimo aceitável</h3>"
                    "<pre><code>spec:\n"
                    "  containers:\n"
                    "  - name: app\n"
                    "    securityContext:\n"
                    "      runAsNonRoot: true\n"
                    "      runAsUser: 65532\n"
                    "      runAsGroup: 65532\n"
                    "      readOnlyRootFilesystem: true\n"
                    "      allowPrivilegeEscalation: false\n"
                    "      capabilities:\n"
                    "        drop: [\"ALL\"]\n"
                    "        # add: [\"NET_BIND_SERVICE\"]  # se realmente precisar\n"
                    "  securityContext:\n"
                    "    seccompProfile:\n"
                    "      type: RuntimeDefault\n"
                    "    fsGroup: 65532</code></pre>"
                    "<p>Por que cada flag:</p>"
                    "<ul>"
                    "<li><strong>runAsNonRoot</strong>: container UID 0 = root no host (a menos "
                    "que use user namespace, ainda alpha em K8s 1.30).</li>"
                    "<li><strong>readOnlyRootFilesystem</strong>: força app a usar volumes "
                    "específicos para escrita. Atacante não escreve binário em /usr/bin.</li>"
                    "<li><strong>allowPrivilegeEscalation: false</strong>: impede setuid binary "
                    "escalation.</li>"
                    "<li><strong>capabilities drop ALL</strong>: app web não precisa nem de "
                    "<code>NET_RAW</code>. Adicione apenas o estritamente necessário.</li>"
                    "<li><strong>seccompProfile: RuntimeDefault</strong>: filtra ~70 syscalls "
                    "perigosas (mount, ptrace, etc.).</li>"
                    "</ul>"

                    "<h3>5. NetworkPolicy default-deny</h3>"
                    "<p>Sem NP, comprometimento de um pod abre o cluster inteiro. Mínimo:</p>"
                    "<pre><code>apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata:\n"
                    "  name: default-deny-all\n"
                    "  namespace: prod\n"
                    "spec:\n"
                    "  podSelector: {}\n"
                    "  policyTypes: [Ingress, Egress]\n"
                    "---\n"
                    "# permitir DNS para todo pod\n"
                    "apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata: { name: allow-dns, namespace: prod }\n"
                    "spec:\n"
                    "  podSelector: {}\n"
                    "  egress:\n"
                    "  - to:\n"
                    "    - namespaceSelector:\n"
                    "        matchLabels: { kubernetes.io/metadata.name: kube-system }\n"
                    "      podSelector:\n"
                    "        matchLabels: { k8s-app: kube-dns }\n"
                    "    ports:\n"
                    "    - protocol: UDP\n"
                    "      port: 53</code></pre>"
                    "<p>Detalhes em 5.3. Aqui o ponto: ative.</p>"

                    "<h3>6. Encryption at rest no etcd</h3>"
                    "<p>etcd guarda Secrets, ConfigMaps, todo o estado. Sem encryption, dump "
                    "do etcd = todos os segredos do cluster em texto claro (apenas base64).</p>"
                    "<p>Configure no kube-apiserver:</p>"
                    "<pre><code># encryption-config.yaml\n"
                    "apiVersion: apiserver.config.k8s.io/v1\n"
                    "kind: EncryptionConfiguration\n"
                    "resources:\n"
                    "- resources:\n"
                    "  - secrets\n"
                    "  providers:\n"
                    "  - kms:\n"
                    "      name: aws-kms\n"
                    "      endpoint: unix:///var/run/kmsplugin/socket\n"
                    "      cachesize: 1000\n"
                    "  - identity: {}  # fallback (sem cripto)</code></pre>"
                    "<p>Em EKS/GKE/AKS, basta marcar opção 'KMS encryption' no cluster. "
                    "Self-hosted exige configurar plugin KMS ou usar provedor <code>aescbc</code> "
                    "com chave gerenciada por você.</p>"

                    "<h3>7. Audit log</h3>"
                    "<p>Audit log registra cada chamada à API. Em incidente, é o que conta a "
                    "história de 'quem fez o quê quando'.</p>"
                    "<pre><code># audit-policy.yaml\n"
                    "apiVersion: audit.k8s.io/v1\n"
                    "kind: Policy\n"
                    "rules:\n"
                    "# secrets/configmaps: log corpo da request/response\n"
                    "- level: RequestResponse\n"
                    "  resources:\n"
                    "  - group: \"\"\n"
                    "    resources: [secrets, configmaps]\n"
                    "# tudo mais: só metadata\n"
                    "- level: Metadata\n"
                    "  omitStages: [RequestReceived]</code></pre>"
                    "<p>Mande para SIEM (Splunk, Datadog, ELK). Em cloud gerenciado, normalmente "
                    "vai automático para CloudWatch/Cloud Logging.</p>"

                    "<h3>8. ServiceAccount tokens</h3>"
                    "<p>Por padrão, todo pod monta o token da SA <code>default</code> em "
                    "<code>/var/run/secrets/kubernetes.io/serviceaccount/</code>. Atacante "
                    "no pod usa esse token para falar com a API. Mitigações:</p>"
                    "<ul>"
                    "<li>Pod que <em>não</em> precisa falar com API: "
                    "<code>automountServiceAccountToken: false</code> no PodSpec ou na SA.</li>"
                    "<li>Pod que precisa: SA dedicada com RBAC mínimo (não use <code>default</code>).</li>"
                    "<li>Bound tokens (K8s 1.21+): TTL curto, audience-bound. Default em SAs novas.</li>"
                    "</ul>"
                    "<pre><code>apiVersion: v1\n"
                    "kind: ServiceAccount\n"
                    "metadata: { name: web, namespace: prod }\n"
                    "automountServiceAccountToken: false  # default off\n"
                    "---\n"
                    "apiVersion: apps/v1\n"
                    "kind: Deployment\n"
                    "metadata: { name: web, namespace: prod }\n"
                    "spec:\n"
                    "  template:\n"
                    "    spec:\n"
                    "      serviceAccountName: web\n"
                    "      automountServiceAccountToken: false  # explícito\n"
                    "      # ...</code></pre>"

                    "<h3>9. Image hardening</h3>"
                    "<ul>"
                    "<li>Pin imagens por digest (<code>@sha256:...</code>), não por tag mutável.</li>"
                    "<li>Use bases distroless / chainguard / wolfi: zero shell, zero pacote "
                    "extra, superfície mínima.</li>"
                    "<li>Scan contínuo no registry (Trivy, Grype, ECR Scan, GAR Vulnerability "
                    "Scanning).</li>"
                    "<li>Verifique assinaturas (Cosign + admission webhook).</li>"
                    "<li>Anexar SBOM (ver tópico 4.5).</li>"
                    "</ul>"

                    "<h3>10. Multi-tenancy</h3>"
                    "<p>Namespace é isolamento <em>fraco</em>. Tenants compartilhando cluster "
                    "exigem várias camadas:</p>"
                    "<ul>"
                    "<li><strong>RBAC</strong> por namespace.</li>"
                    "<li><strong>NetworkPolicy</strong> default-deny por NS.</li>"
                    "<li><strong>ResourceQuota</strong>: limite de CPU/RAM/objetos por NS "
                    "(senão um tenant come o cluster).</li>"
                    "<li><strong>LimitRange</strong>: defaults de requests/limits para pods.</li>"
                    "<li><strong>PSS restricted</strong>.</li>"
                    "<li><strong>Node isolation</strong> via taints + tolerations + nodeSelector "
                    "(tenant em nodes dedicados).</li>"
                    "<li><strong>Hierarchical Namespaces</strong> (HNC) para org grande.</li>"
                    "</ul>"
                    "<p>Tenants <em>realmente</em> hostis (PaaS multi-cliente)? Cluster por "
                    "tenant, não namespace.</p>"

                    "<h3>11. Auditoria automatizada</h3>"
                    "<ul>"
                    "<li><strong>kube-bench</strong>: avalia cluster contra CIS Benchmark. "
                    "Rode em CronJob noturno; falhas High abrem ticket.</li>"
                    "<li><strong>kubescape</strong>: NSA/CISA + MITRE ATT&amp;CK + CIS. UI bonita.</li>"
                    "<li><strong>Trivy K8s</strong>: scan de manifests + RBAC + workloads.</li>"
                    "<li><strong>kubeaudit / polaris</strong>: linting de manifests.</li>"
                    "<li><strong>Falco</strong> (runtime) / <strong>Tetragon</strong>: ver 5.6.</li>"
                    "</ul>"
                    "<pre><code># Exemplo: rode kube-bench em CronJob\n"
                    "$ kubectl apply -f https://raw.githubusercontent.com/aquasecurity/"
                    "kube-bench/main/job.yaml\n"
                    "$ kubectl logs job/kube-bench</code></pre>"

                    "<h3>12. Cluster API server: o castelo do reino</h3>"
                    "<ul>"
                    "<li>Acesso ao apiserver via private endpoint (não exposto à internet) "
                    "sempre que possível.</li>"
                    "<li>OIDC para autenticação humana (Google Workspace, Okta, Azure AD).</li>"
                    "<li>MFA obrigatório no IdP, não no kubeconfig.</li>"
                    "<li>Bind kubeconfig ao laptop do humano (curto TTL, refresh via OIDC).</li>"
                    "<li>SSH no node? Em cloud, prefira SSM/IAP. Self-hosted, bastion + chave "
                    "ed25519, 2FA na bastion.</li>"
                    "</ul>"

                    "<h3>13. Backup e disaster recovery</h3>"
                    "<ul>"
                    "<li><strong>etcd snapshot</strong> diário em local seguro: <code>etcdctl "
                    "snapshot save snap.db</code>.</li>"
                    "<li><strong>Velero</strong>: backup de objetos + PVs. Pode restore "
                    "cross-cluster.</li>"
                    "<li>Teste restore. Backup não-testado é wishful thinking.</li>"
                    "</ul>"

                    "<h3>14. Anti-patterns frequentes em hardening</h3>"
                    "<ul>"
                    "<li><strong>Tudo cluster-admin para CI</strong>: comprometeu CI = todo o cluster.</li>"
                    "<li><strong>SA default com RoleBinding amplo</strong>: pod random vira admin.</li>"
                    "<li><strong>Sem audit-log</strong>: incidente = olhar para o nada.</li>"
                    "<li><strong>'Vamos fazer hardening depois'</strong>: dívida técnica de "
                    "segurança que cresce com o cluster.</li>"
                    "<li><strong>kube-bench rodado uma vez</strong>: drift volta. Automatize.</li>"
                    "</ul>"

                    "<h3>15. Roadmap pragmático</h3>"
                    "<p>Em ordem de impacto:</p>"
                    "<ol>"
                    "<li>RBAC: revisar quem é cluster-admin. Reduzir.</li>"
                    "<li>PSS restricted em namespaces de prod.</li>"
                    "<li>NetworkPolicy default-deny.</li>"
                    "<li>Encryption at rest no etcd.</li>"
                    "<li>SecurityContext em todos os Deployments.</li>"
                    "<li>kube-bench em CI noturno + tickets para findings High.</li>"
                    "<li>Audit log → SIEM.</li>"
                    "<li>Image scan + signing.</li>"
                    "<li>Runtime security (Falco).</li>"
                    "</ol>"
                ),
                "practical": (
                    "Em cluster local, rode <code>kube-bench run --targets master,node</code>. "
                    "Identifique 3 findings High e corrija (ex.: <code>--anonymous-auth=false</code>). "
                    "Aplique label <code>pod-security.kubernetes.io/enforce=restricted</code> em "
                    "um namespace e tente subir um pod com <code>privileged: true</code>, "
                    "confirme rejeição. Por fim, crie um Deployment com securityContext completo "
                    "(runAsNonRoot, readOnlyRootFilesystem, drop ALL caps) e debug os erros até "
                    "rodar limpo."
                ),
            },
            "materials": [
                m("CIS Kubernetes Benchmark", "https://www.cisecurity.org/benchmark/kubernetes", "docs", ""),
                m("kube-bench", "https://github.com/aquasecurity/kube-bench", "tool", ""),
                m("Pod Security Standards", "https://kubernetes.io/docs/concepts/security/pod-security-standards/", "docs", ""),
                m("RBAC docs", "https://kubernetes.io/docs/reference/access-authn-authz/rbac/", "docs", ""),
                m("NSA/CISA Kubernetes Hardening Guide", "https://www.cisa.gov/sites/default/files/publications/Kubernetes_Hardening_Guide_1.2.pdf", "docs", ""),
                m("Kubescape", "https://kubescape.io/", "tool", "Validação CIS + NSA."),
                m("Trivy K8s", "https://aquasecurity.github.io/trivy/latest/docs/target/kubernetes/", "tool", ""),
            ],
            "questions": [
                q("RBAC em K8s:",
                  "Concede permissões via Roles/ClusterRoles + Bindings.",
                  ["Substitui cluster.", "Apenas para nodes.", "Apenas para pods."],
                  "Aplique para SAs (apps), usuários e grupos. Audit com kubectl auth can-i."),
                q("PodSecurity 'restricted':",
                  "Política mais segura disponível por padrão.",
                  ["Permite root sempre.", "Sem proteção.", "Só funciona em GKE."],
                  "Bloqueia hostPath, privileged, runAsRoot, hostNetwork, hostPID etc."),
                q("NetworkPolicy default deny:",
                  "Boa prática para limitar tráfego inter-pods.",
                  ["Bloqueia o cluster.", "Apaga pods.", "Aumenta CPU."],
                  "Sem NP, qualquer pod compromisso vira pivot para todo o cluster."),
                q("Secrets em etcd:",
                  "Devem ser criptografados em repouso (KMS).",
                  ["Já são por default.", "Não importam.", "Apenas em prod."],
                  "Por padrão, Secret é só base64 no etcd. Configure EncryptionConfiguration."),
                q("Audit logs em K8s:",
                  "Registram ações na API server.",
                  ["Substituem métricas.", "Apenas para Pods.", "Apenas DNS."],
                  "Configure política em audit-policy.yaml e envie para SIEM externo."),
                q("kube-bench faz:",
                  "Avalia cluster contra CIS Benchmark.",
                  ["Atualiza nodes.", "Aplica patches.", "Substitui RBAC."],
                  "Rode periodicamente; integre saída ao CI/CD para barrar merges sem fix."),
                q("ServiceAccount default:",
                  "Não deve montar token automaticamente em todo pod.",
                  ["Sempre montar.", "Não tem token.", "Substitui IAM."],
                  "Set `automountServiceAccountToken: false` quando o pod não precisa falar com API."),
                q("Cluster admin:",
                  "Restringir uso a engenheiros estritos com MFA.",
                  ["Conceder a todos.", "Sem necessidade.", "Apenas para CI."],
                  "Cluster-admin é equivalente a root no cluster. Acesso break-glass auditado."),
                q("Image pull secret:",
                  "Permite pull de registry privado.",
                  ["Apaga imagens.", "Substitui RBAC.", "Apenas DNS."],
                  "Configure em SA da app via imagePullSecrets. Em cloud, IRSA/Workload Identity > secret estático."),
                q("Container privilegiado:",
                  "Tem ~root no host, evite ao máximo.",
                  ["Mais rápido.", "Mais seguro.", "Necessário sempre."],
                  "Apenas casos justificados (CNI agent, GPU driver). Bloqueie em policy padrão."),
            ],
        },
        # =====================================================================
        # 5.3 Network Policies
        # =====================================================================
        {
            "title": "Network Policies",
            "summary": "Controlar quem fala com quem dentro do cluster.",
            "lesson": {
                "intro": (
                    "Em K8s default, todo pod conversa com todo pod. NetworkPolicy muda isso. "
                    "Sem NP, comprometer um pod = pivotar livremente pelo cluster, cenário "
                    "clássico de movimento lateral em quase todo breach reportado em K8s. "
                    "NetworkPolicy é o firewall L3/L4 do cluster, declarativo e por label. "
                    "Aprender a escrevê-las bem é uma das maiores alavancas de defesa."
                ),
                "body": (
                    "<h3>1. Como NP funciona por baixo</h3>"
                    "<p>NP é um <em>objeto K8s</em>. O API server aceita o YAML e armazena no "
                    "etcd. Quem efetivamente <em>aplica</em> as regras é o <strong>CNI plugin</strong>. "
                    "Se o CNI não suporta NP (default kubenet, flannel sem add-on), o objeto "
                    "vira <em>YAML decorativo</em>: existe, mas ninguém liga. Use Calico, Cilium, "
                    "Antrea, Weave em prod.</p>"
                    "<p>O CNI traduz NP em iptables, ipvs, eBPF, ou o que ele usar. Você não "
                    "precisa pensar nisso, só saber que tem que estar lá.</p>"

                    "<h3>2. Anatomia de uma NP</h3>"
                    "<pre><code>apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata:\n"
                    "  name: api-allow-web\n"
                    "  namespace: prod\n"
                    "spec:\n"
                    "  podSelector:\n"
                    "    matchLabels: { app: api }       # quem é alvo desta política\n"
                    "  policyTypes: [Ingress, Egress]    # qual direção\n"
                    "  ingress:\n"
                    "  - from:\n"
                    "    - podSelector:\n"
                    "        matchLabels: { app: web }   # quem pode entrar\n"
                    "    ports:\n"
                    "    - protocol: TCP\n"
                    "      port: 8080\n"
                    "  egress:\n"
                    "  - to:\n"
                    "    - namespaceSelector:\n"
                    "        matchLabels: { kubernetes.io/metadata.name: kube-system }\n"
                    "      podSelector:\n"
                    "        matchLabels: { k8s-app: kube-dns }\n"
                    "    ports:\n"
                    "    - protocol: UDP\n"
                    "      port: 53\n"
                    "  - to:\n"
                    "    - podSelector:\n"
                    "        matchLabels: { app: postgres }\n"
                    "    ports:\n"
                    "    - protocol: TCP\n"
                    "      port: 5432</code></pre>"
                    "<p>Pontos importantes:</p>"
                    "<ul>"
                    "<li><code>podSelector: {}</code> (vazio) = <em>todos</em> os pods do "
                    "namespace.</li>"
                    "<li>NP é <strong>aditivo</strong>: múltiplas políticas se somam. Não há "
                    "regra de prioridade, qualquer NP que permita um fluxo, permite.</li>"
                    "<li>Default: se nenhuma NP atinge um pod, <em>tudo é permitido</em>. Se "
                    "qualquer NP atinge, default é <em>deny tudo</em> exceto o que ela permite.</li>"
                    "<li>NP padrão é <strong>L3/L4</strong> (IP + porta). Para L7 (paths HTTP, "
                    "métodos), use Cilium NP ou service mesh.</li>"
                    "</ul>"

                    "<h3>3. Default-deny por namespace</h3>"
                    "<p>Padrão de prod:</p>"
                    "<pre><code>apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata:\n"
                    "  name: default-deny\n"
                    "  namespace: prod\n"
                    "spec:\n"
                    "  podSelector: {}\n"
                    "  policyTypes: [Ingress, Egress]\n"
                    "# sem `ingress` nem `egress` = nada é permitido</code></pre>"
                    "<p>Aplicado isolado, esse NP bloqueia <em>tudo</em>, inclusive DNS, "
                    "telemetria, registry. Você precisa adicionar regras de exceção para fluxos "
                    "válidos.</p>"

                    "<h3>4. Permita DNS sempre</h3>"
                    "<p>Pod sem egress para kube-dns não resolve nomes. Sintoma: app reclama "
                    "'Name or service not known' a cada conexão. Solução universal:</p>"
                    "<pre><code>apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata:\n"
                    "  name: allow-dns\n"
                    "  namespace: prod\n"
                    "spec:\n"
                    "  podSelector: {}\n"
                    "  policyTypes: [Egress]\n"
                    "  egress:\n"
                    "  - to:\n"
                    "    - namespaceSelector:\n"
                    "        matchLabels: { kubernetes.io/metadata.name: kube-system }\n"
                    "      podSelector:\n"
                    "        matchLabels: { k8s-app: kube-dns }\n"
                    "    ports:\n"
                    "    - protocol: UDP\n"
                    "      port: 53\n"
                    "    - protocol: TCP\n"
                    "      port: 53</code></pre>"

                    "<h3>5. Selectors: a parte que confunde</h3>"
                    "<p>Há quatro 'tipos' de matching:</p>"
                    "<ul>"
                    "<li><strong>podSelector</strong>: filtra por label do pod (mesmo namespace).</li>"
                    "<li><strong>namespaceSelector</strong>: filtra por label do namespace.</li>"
                    "<li><strong>podSelector + namespaceSelector</strong> dentro de um mesmo "
                    "elemento: AND (label do pod E label do NS).</li>"
                    "<li><strong>ipBlock</strong>: por CIDR (geralmente para egress externo).</li>"
                    "</ul>"
                    "<p>Combinatória crítica:</p>"
                    "<pre><code>ingress:\n"
                    "- from:\n"
                    "  - namespaceSelector: { matchLabels: { env: prod } }\n"
                    "    podSelector: { matchLabels: { app: web } }\n"
                    "# regra acima: pod E ns combinados (AND)\n"
                    "\n"
                    "ingress:\n"
                    "- from:\n"
                    "  - namespaceSelector: { matchLabels: { env: prod } }\n"
                    "  - podSelector: { matchLabels: { app: web } }\n"
                    "# regra acima: pod OU ns (OR, dois itens da lista from)</code></pre>"
                    "<p>Erro fácil de cometer; teste sempre.</p>"

                    "<h3>6. Egress: o controle mais subestimado</h3>"
                    "<p>NP de Ingress é o que todo mundo escreve. Egress é onde você ganha "
                    "muito mais segurança e quase ninguém escreve. Pod comprometido sem egress "
                    "controlado:</p>"
                    "<ul>"
                    "<li>não exfiltra dados para C2 (command &amp; control) externo;</li>"
                    "<li>não pivota para outros pods do cluster;</li>"
                    "<li>não baixa malware adicional do registry público.</li>"
                    "</ul>"
                    "<p>Estratégia em camadas:</p>"
                    "<ol>"
                    "<li>Default-deny egress.</li>"
                    "<li>Permita DNS (kube-dns).</li>"
                    "<li>Permita destinos internos necessários (DB, cache, outros services).</li>"
                    "<li>Para internet: roteie por proxy de saída (squid, ZTNA) que aplica "
                    "allowlist de domínios e gera log auditável.</li>"
                    "</ol>"
                    "<pre><code># exemplo: pod web só fala com api e DNS\n"
                    "apiVersion: networking.k8s.io/v1\n"
                    "kind: NetworkPolicy\n"
                    "metadata: { name: web-egress, namespace: prod }\n"
                    "spec:\n"
                    "  podSelector: { matchLabels: { app: web } }\n"
                    "  policyTypes: [Egress]\n"
                    "  egress:\n"
                    "  - to:\n"
                    "    - podSelector: { matchLabels: { app: api } }\n"
                    "    ports: [{ protocol: TCP, port: 8080 }]\n"
                    "  - to:\n"
                    "    - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }\n"
                    "      podSelector: { matchLabels: { k8s-app: kube-dns } }\n"
                    "    ports: [{ protocol: UDP, port: 53 }]</code></pre>"

                    "<h3>7. Cilium Network Policies (CNP)</h3>"
                    "<p>Cilium estende NP padrão com Layer 7 (HTTP, gRPC, Kafka, DNS) e "
                    "matching por identidade SPIFFE/FQDN:</p>"
                    "<pre><code>apiVersion: cilium.io/v2\n"
                    "kind: CiliumNetworkPolicy\n"
                    "metadata: { name: api-l7, namespace: prod }\n"
                    "spec:\n"
                    "  endpointSelector: { matchLabels: { app: api } }\n"
                    "  ingress:\n"
                    "  - fromEndpoints:\n"
                    "    - matchLabels: { app: web }\n"
                    "    toPorts:\n"
                    "    - ports: [{ port: \"8080\", protocol: TCP }]\n"
                    "      rules:\n"
                    "        http:\n"
                    "        - method: GET\n"
                    "          path: \"/api/v1/users\"\n"
                    "        - method: GET\n"
                    "          path: \"/api/v1/orders/[0-9]+\"\n"
                    "  egress:\n"
                    "  - toFQDNs:\n"
                    "    - matchPattern: \"*.googleapis.com\"\n"
                    "    toPorts:\n"
                    "    - ports: [{ port: \"443\", protocol: TCP }]</code></pre>"
                    "<p>'Web pode chamar GET /api/v1/users em api, mas não DELETE'. Útil para "
                    "limitar capacidade de pivot mesmo dentro de fluxo permitido.</p>"

                    "<h3>8. Observabilidade: o ponto cego</h3>"
                    "<p>NP rejeita silenciosamente, o pacote some. App reclama 'connection "
                    "refused', você não sabe se foi NP, kube-proxy, app down. Ferramentas:</p>"
                    "<ul>"
                    "<li><strong>Cilium Hubble</strong>: stream de fluxos permitidos/negados "
                    "em tempo real. CLI e UI.</li>"
                    "<li><strong>Calico Felix logs</strong>: configurável.</li>"
                    "<li><strong>tcpdump no pod</strong> (com NET_ADMIN ou debug container) "
                    "para ver se pacote sai.</li>"
                    "<li><strong>kubectl exec ... -- nc -zv host port</strong> para testar.</li>"
                    "</ul>"
                    "<p>Estratégia: rode em modo <em>audit-only</em> primeiro (Calico tem flag, "
                    "Cilium tem <code>policyEnforcementMode: never</code>), capture violações, "
                    "ajuste, depois enforce.</p>"

                    "<h3>9. Padrão de implantação seguro</h3>"
                    "<ol>"
                    "<li>Cluster novo: aplique NP <em>permissivas</em> em todos NS de prod "
                    "(<code>allow-all</code>).</li>"
                    "<li>Para um NS de cada vez: substitua por default-deny + regras necessárias.</li>"
                    "<li>Use Hubble/Felix para validar 'nada está sendo bloqueado errado'.</li>"
                    "<li>Mova para o próximo NS.</li>"
                    "<li>Após estabilizar, escreva CI policy: 'todo NS de prod deve ter "
                    "default-deny'.</li>"
                    "</ol>"

                    "<h3>10. Controle de tráfego para fora do cluster</h3>"
                    "<p>NP padrão usa <code>ipBlock</code> com CIDRs:</p>"
                    "<pre><code>egress:\n"
                    "- to:\n"
                    "  - ipBlock:\n"
                    "      cidr: 10.0.0.0/8         # rede interna corporativa\n"
                    "      except: [10.0.99.0/24]   # exceto subnet sensível\n"
                    "  ports: [{ protocol: TCP, port: 443 }]</code></pre>"
                    "<p>Limitação: IPs externos mudam (S3, APIs SaaS). Por isso Cilium FQDN "
                    "(<code>toFQDNs</code>) é mais robusto para destinos cloud.</p>"

                    "<h3>11. Multi-cluster e service mesh</h3>"
                    "<p>NP funciona dentro do cluster. Para tráfego entre clusters (multi-region, "
                    "multi-cloud), você precisa de service mesh (Istio, Linkerd, Cilium "
                    "ClusterMesh) que dá identidade comum + mTLS + AuthZ por carga. Tópico 5.5 "
                    "(Zero Trust) cobre isso.</p>"

                    "<h3>12. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>NP só de ingress</strong>: deixa egress livre = exfiltração "
                    "tranquila.</li>"
                    "<li><strong>Esquecer DNS</strong>: app quebra silenciosamente.</li>"
                    "<li><strong>Selector AND vs OR confuso</strong>: regra acidentalmente "
                    "permissiva.</li>"
                    "<li><strong>Sem CNI compatível</strong>: NP existe mas não enforça.</li>"
                    "<li><strong>NetworkPolicy no <code>kube-system</code></strong>: pode quebrar "
                    "DNS, CNI, ingress controller. Use com cuidado e testes.</li>"
                    "<li><strong>NP labels que viram com renaming</strong>: app foi renomeada, "
                    "NP não foi atualizada, fluxo passou a fluir/parar de fluir silenciosamente.</li>"
                    "</ul>"

                    "<h3>13. Validação automatizada</h3>"
                    "<ul>"
                    "<li><strong>NetworkPolicy editor</strong> (editor.networkpolicy.io): UI "
                    "visual.</li>"
                    "<li><strong>cnp-checker</strong>, <strong>kubectl-np-viewer</strong>: "
                    "valida regras.</li>"
                    "<li><strong>kyverno/gatekeeper</strong>: policy 'todo NS deve ter "
                    "default-deny NP'.</li>"
                    "<li><strong>Hubble</strong> para validar continuamente em prod.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Em cluster com Cilium ou Calico, aplique <code>default-deny</code> em um NS "
                    "de teste, depois <code>allow-dns</code>, depois NP permitindo ingress de um "
                    "pod 'web' para um pod 'api'. Use <code>kubectl exec</code> + <code>nc -zv</code> "
                    "para validar bloqueios e permissões. Por fim, instale Hubble e veja fluxos "
                    "permitidos/negados em tempo real."
                ),
            },
            "materials": [
                m("Kubernetes NetworkPolicy", "https://kubernetes.io/docs/concepts/services-networking/network-policies/", "docs", ""),
                m("Calico", "https://docs.tigera.io/calico/latest/about", "docs", ""),
                m("Cilium", "https://docs.cilium.io/", "docs", ""),
                m("NetworkPolicy editor", "https://editor.networkpolicy.io/", "tool", ""),
                m("Cilium Cheat Sheet", "https://docs.cilium.io/en/stable/cheatsheet/", "docs", ""),
                m("Hubble (visualização)", "https://github.com/cilium/hubble", "tool", ""),
                m("Kubernetes Network Policy Recipes", "https://github.com/ahmetb/kubernetes-network-policy-recipes", "course", "Exemplos para copiar."),
            ],
            "questions": [
                q("Sem NetworkPolicy:",
                  "Tráfego é totalmente permitido entre pods.",
                  ["Tudo bloqueado.", "Apenas TCP 80.", "Apenas mesmo namespace."],
                  "Pod comprometido pode atacar qualquer outro, base de muitos breaches em K8s."),
                q("NP é avaliado no:",
                  "CNI plugin do cluster (Calico/Cilium etc.).",
                  ["kube-proxy.", "Ingress.", "API server."],
                  "Sem CNI compatível, NP é apenas YAML decorativo."),
                q("Default deny ingress:",
                  "Bloqueia tráfego de entrada exceto regras explícitas.",
                  ["Bloqueia o pod.", "Aumenta CPU.", "Substitui RBAC."],
                  "Comece com deny-all e libere o que app realmente precisa."),
                q("Selecionador por label:",
                  "Permite políticas dinâmicas conforme deploy.",
                  ["Apenas por IP fixo.", "Apenas pelo nome.", "Apenas em DaemonSet."],
                  "IPs em K8s mudam todo deploy. Labels seguem a app."),
                q("Cilium adiciona:",
                  "Observabilidade e Layer 7 policies via eBPF.",
                  ["Apenas IPv6.", "Apenas DNS.", "Substitui K8s."],
                  "Permite restringir métodos HTTP, paths, gRPC services etc."),
                q("NP NS-to-NS:",
                  "Selecione namespaces via namespaceSelector.",
                  ["Não é possível.", "Apenas no mesmo NS.", "Apenas em prod."],
                  "Use labels nos namespaces (ex.: env=prod) e selecione por elas."),
                q("Egress policy:",
                  "Limita destinos que pod pode acessar.",
                  ["Apenas TLS.", "Apenas DNS.", "Apenas headers."],
                  "Crítico para reduzir exfiltração. Combine com proxy de saída."),
                q("DNS pode ser quebrado se:",
                  "Egress não permitir kube-dns explicitamente.",
                  ["Sempre funciona.", "Não depende.", "É opcional."],
                  "Lembre-se: porta 53 UDP/TCP para kube-dns no namespace kube-system."),
                q("Cilium Hubble:",
                  "Observabilidade do tráfego do cluster.",
                  ["Substitui Argo.", "Roteador.", "Backup."],
                  "Mostra fluxos permitidos/negados em tempo real. Útil para debug de NP."),
                q("NP é:",
                  "Aditivo, múltiplas regras se acumulam.",
                  ["Substitutivo.", "Apenas uma por NS.", "Apenas global."],
                  "Cada NP soma; final é union. Ordem não importa."),
            ],
        },
        # =====================================================================
        # 5.4 Admission Controllers
        # =====================================================================
        {
            "title": "Admission Controllers",
            "summary": "Impedir que containers inseguros sejam criados.",
            "lesson": {
                "intro": (
                    "Toda configuração crítica começa com 'kubectl apply' bem-sucedido, e termina "
                    "com 'eu não sabia que dava pra fazer isso'. Admission controllers são a "
                    "última linha entre a intenção do usuário e a gravação no etcd. Você não "
                    "trata <em>descuido</em> com admission; você impede que descuido cause "
                    "estrago. Hoje, em prod séria, é não-negociável: PSS + Kyverno/Gatekeeper "
                    "deveria estar em todo cluster."
                ),
                "body": (
                    "<h3>1. O fluxo no API server</h3>"
                    "<p>Quando você faz <code>kubectl apply</code>, o request percorre fases:</p>"
                    "<ol>"
                    "<li><strong>Autenticação</strong>: quem é você? (cert, OIDC, token)</li>"
                    "<li><strong>Autorização</strong>: o que você pode fazer? (RBAC)</li>"
                    "<li><strong>Mutating Admission</strong>: o request pode ser <em>alterado</em> "
                    "antes de salvar (ex.: injetar sidecar Istio, definir defaults).</li>"
                    "<li><strong>Schema validation</strong>: YAML conforma com a CRD?</li>"
                    "<li><strong>Validating Admission</strong>: o request <em>passa</em> nas "
                    "regras de negócio? (sem alterar)</li>"
                    "<li><strong>Persist no etcd</strong>.</li>"
                    "</ol>"
                    "<p>Se qualquer admission rejeita, etcd não é tocado, usuário recebe erro.</p>"

                    "<h3>2. Tipos de admission</h3>"
                    "<ul>"
                    "<li><strong>Built-in</strong>: compilados no apiserver. Ex.: "
                    "<code>NamespaceLifecycle</code>, <code>LimitRanger</code>, "
                    "<code>ResourceQuota</code>, <code>ServiceAccount</code>, "
                    "<code>PodSecurity</code> (PSS).</li>"
                    "<li><strong>Webhook externo</strong>: você define um webhook HTTPS; "
                    "apiserver faz POST com o request, espera resposta. Mutating ou Validating.</li>"
                    "<li><strong>Validating Admission Policy</strong> (K8s 1.30 GA): policies "
                    "em CEL declaradas como CRD, sem precisar webhook externo. Mais leve.</li>"
                    "</ul>"

                    "<h3>3. Engines populares</h3>"
                    "<ul>"
                    "<li><strong>Kyverno</strong> (CNCF Incubating): policies em YAML, "
                    "K8s-native. Validating, mutating, generating, cleanup. Curva rasa.</li>"
                    "<li><strong>OPA Gatekeeper</strong> (CNCF Graduated): OPA + Rego. "
                    "Modelo CRD: <code>ConstraintTemplate</code> define regra; "
                    "<code>Constraint</code> instancia.</li>"
                    "<li><strong>jsPolicy</strong>: policies em TypeScript.</li>"
                    "<li><strong>Validating Admission Policy</strong> (in-tree): CEL, sem deps "
                    "externas. Caminho do futuro.</li>"
                    "</ul>"

                    "<h3>4. Exemplo Kyverno: bloquear :latest</h3>"
                    "<pre><code>apiVersion: kyverno.io/v1\n"
                    "kind: ClusterPolicy\n"
                    "metadata: { name: disallow-latest-tag }\n"
                    "spec:\n"
                    "  validationFailureAction: Enforce\n"
                    "  background: true\n"
                    "  rules:\n"
                    "  - name: require-image-tag\n"
                    "    match:\n"
                    "      any:\n"
                    "      - resources:\n"
                    "          kinds: [Pod]\n"
                    "    validate:\n"
                    "      message: \"Imagens devem ter tag explícita (não :latest).\"\n"
                    "      pattern:\n"
                    "        spec:\n"
                    "          containers:\n"
                    "          - image: \"!*:latest\"</code></pre>"

                    "<h3>5. Exemplo Gatekeeper: exigir labels</h3>"
                    "<pre><code># ConstraintTemplate (Rego)\n"
                    "apiVersion: templates.gatekeeper.sh/v1\n"
                    "kind: ConstraintTemplate\n"
                    "metadata: { name: requiredlabels }\n"
                    "spec:\n"
                    "  crd:\n"
                    "    spec:\n"
                    "      names: { kind: RequiredLabels }\n"
                    "      validation:\n"
                    "        openAPIV3Schema:\n"
                    "          type: object\n"
                    "          properties:\n"
                    "            labels: { type: array, items: { type: string } }\n"
                    "  targets:\n"
                    "  - target: admission.k8s.gatekeeper.sh\n"
                    "    rego: |\n"
                    "      package requiredlabels\n"
                    "      violation[{\"msg\": msg}] {\n"
                    "        required := input.parameters.labels\n"
                    "        provided := input.review.object.metadata.labels\n"
                    "        missing := required[_]\n"
                    "        not provided[missing]\n"
                    "        msg := sprintf(\"Label obrigatória '%s' ausente\", [missing])\n"
                    "      }\n"
                    "---\n"
                    "# Constraint (instância)\n"
                    "apiVersion: constraints.gatekeeper.sh/v1beta1\n"
                    "kind: RequiredLabels\n"
                    "metadata: { name: ns-must-have-owner }\n"
                    "spec:\n"
                    "  match:\n"
                    "    kinds:\n"
                    "    - apiGroups: [\"\"]\n"
                    "      kinds: [Namespace]\n"
                    "  parameters:\n"
                    "    labels: [owner, team, costcenter]</code></pre>"

                    "<h3>6. Casos de uso típicos</h3>"
                    "<ul>"
                    "<li>Bloquear imagens com tag <code>latest</code> ou de registries não "
                    "autorizados.</li>"
                    "<li>Exigir <code>resources.requests/limits</code>.</li>"
                    "<li>Exigir labels obrigatórias (owner, team, costcenter, env).</li>"
                    "<li>Bloquear <code>hostPath</code>, <code>privileged</code>, "
                    "<code>runAsRoot</code>.</li>"
                    "<li>Verificar assinatura Cosign de imagens com sigstore policy controller.</li>"
                    "<li>Auto-injetar sidecars (Istio, Linkerd, Vault Agent) com mutating webhook.</li>"
                    "<li>Forçar PVC com storageClass específico.</li>"
                    "<li>Garantir que Service do tipo LoadBalancer tem annotation de subnet "
                    "interna.</li>"
                    "<li>Limitar Ingress por host pattern (não permitir <code>*.example.com</code> "
                    "ao acaso).</li>"
                    "</ul>"

                    "<h3>7. Modos: audit, warn, enforce</h3>"
                    "<p>Lance policies de forma incremental:</p>"
                    "<ol>"
                    "<li><strong>audit</strong>: log apenas, sem efeito visível ao usuário. "
                    "Você descobre o que <em>seria</em> bloqueado.</li>"
                    "<li><strong>warn</strong>: o <code>kubectl apply</code> mostra warning "
                    "mas aceita. Times percebem antes de virar bloqueio.</li>"
                    "<li><strong>enforce</strong>: bloqueia. Tem que ser feito após audit + "
                    "warn limpos.</li>"
                    "</ol>"
                    "<p>Sem essa progressão, time rejeita iniciativa no primeiro deploy "
                    "bloqueado e a política é desligada.</p>"

                    "<h3>8. Webhook em produção: cuidados</h3>"
                    "<p>Webhook quebrado pode <em>derrubar o cluster</em>: se apiserver "
                    "depender da resposta e webhook está down, todo apply fica pendurado. "
                    "Mitigações:</p>"
                    "<ul>"
                    "<li><strong>failurePolicy: Ignore</strong> para webhooks não-críticos.</li>"
                    "<li><strong>failurePolicy: Fail</strong> para os críticos (sec), mas "
                    "garanta HA (3+ réplicas, PDB).</li>"
                    "<li><strong>timeoutSeconds</strong>: ≤5s. Webhook lento atrasa cluster.</li>"
                    "<li><strong>namespaceSelector</strong>: exclua <code>kube-system</code> "
                    "e o NS do próprio webhook (você não quer webhook validando si mesmo).</li>"
                    "<li><strong>Runbook 'desligar emergência'</strong>: scripts pré-aprovados "
                    "para deletar webhook em incidente.</li>"
                    "<li>Monitoramento de latência/erro do próprio webhook.</li>"
                    "</ul>"

                    "<h3>9. Sequência: mutating depois validating</h3>"
                    "<p>Mutating roda primeiro. Pode haver vários (Istio injetor, Vault Agent "
                    "injetor, defaults). Ordem entre mutating é não-determinística, escreva "
                    "policies que sejam idempotentes. Validating roda depois e <em>só</em> "
                    "rejeita; objeto final que vai ao etcd é o pós-mutação.</p>"

                    "<h3>10. Verificação de assinaturas (Cosign)</h3>"
                    "<p>Sigstore Policy Controller é admission webhook que valida assinaturas:</p>"
                    "<pre><code>apiVersion: policy.sigstore.dev/v1beta1\n"
                    "kind: ClusterImagePolicy\n"
                    "metadata: { name: signed-by-team }\n"
                    "spec:\n"
                    "  images:\n"
                    "  - glob: ghcr.io/myorg/**\n"
                    "  authorities:\n"
                    "  - keyless:\n"
                    "      url: https://fulcio.sigstore.dev\n"
                    "      identities:\n"
                    "      - issuer: https://token.actions.githubusercontent.com\n"
                    "        subject: https://github.com/myorg/repo/.github/workflows/release.yml@refs/heads/main</code></pre>"
                    "<p>Pod só roda se imagem foi assinada por workflow autorizado em CI. "
                    "Combinação com SBOM/SLSA = supply chain forte.</p>"

                    "<h3>11. Observabilidade de policies</h3>"
                    "<ul>"
                    "<li>Kyverno gera <code>PolicyReport</code> CRDs com violações.</li>"
                    "<li>Gatekeeper expõe métricas Prometheus (constraints violadas, latência).</li>"
                    "<li>Mande para Grafana / SIEM. Regrida-se por NS para mostrar 'qual time "
                    "tem mais violações pendentes'.</li>"
                    "</ul>"

                    "<h3>12. Diferença com runtime security</h3>"
                    "<p>Admission é <em>preventivo</em>, bloqueia antes do recurso existir. "
                    "Não enxerga problemas em runtime. Pod aprovado pode comportar-se mal "
                    "depois (escalation, exfil). Combine com Falco/Tetragon (5.6).</p>"

                    "<h3>13. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Deploy direto em enforce</strong>: time atualiza repo, deploy "
                    "falha, todos param.</li>"
                    "<li><strong>Webhook único, sem HA</strong>: todo cluster depende dele.</li>"
                    "<li><strong>Policy gigante e ambígua</strong>: erros confundem, time "
                    "ignora.</li>"
                    "<li><strong>Sem mensagem clara</strong>: 'denied' não diz como corrigir; "
                    "inclua URL do runbook.</li>"
                    "<li><strong>Policy só em manifests, não nas Helm charts subjacentes</strong>: "
                    "Helm aplica e admission rejeita; release fica corrupted.</li>"
                    "</ul>"

                    "<h3>14. Roadmap pragmático</h3>"
                    "<ol>"
                    "<li>Habilite PSS restricted em prod NS.</li>"
                    "<li>Instale Kyverno (mais fácil) ou Gatekeeper.</li>"
                    "<li>Aplique 5-10 policies básicas em modo <em>audit</em>.</li>"
                    "<li>Mostre relatório semanal aos times.</li>"
                    "<li>Promova para <em>warn</em> depois de 2 semanas.</li>"
                    "<li>Promova para <em>enforce</em> depois de mais 2 semanas.</li>"
                    "<li>Integre verificação de assinatura.</li>"
                    "<li>Adicione policies específicas do seu domínio.</li>"
                    "</ol>"
                ),
                "practical": (
                    "Instale Kyverno via Helm. Aplique policy bloqueando imagens com tag "
                    "<code>:latest</code> em modo <code>audit</code>. Faça <code>kubectl apply</code> "
                    "de um pod com <code>image: nginx:latest</code> e veja o <code>PolicyReport</code>. "
                    "Promova para <code>Enforce</code> e confirme que o apply é rejeitado com "
                    "mensagem clara."
                ),
            },
            "materials": [
                m("Admission Controllers", "https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/", "docs", ""),
                m("Gatekeeper", "https://open-policy-agent.github.io/gatekeeper/website/docs/", "docs", ""),
                m("Kyverno policies", "https://kyverno.io/policies/", "docs", ""),
                m("ImagePolicyWebhook", "https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#imagepolicywebhook", "docs", ""),
                m("OPA Rego playground", "https://play.openpolicyagent.org/", "tool", ""),
                m("Validating Admission Policy", "https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/",
                  "docs", "Alternativa nativa em CEL."),
                m("Sigstore Policy Controller", "https://docs.sigstore.dev/policy-controller/overview/", "docs", "Verificação de assinaturas."),
            ],
            "questions": [
                q("Validating webhook:",
                  "Aprova ou rejeita pedido sem alterá-lo.",
                  ["Sempre altera.", "Apaga recurso.", "Substitui RBAC."],
                  "Mutating altera (ex.: sidecar injection); validating só decide."),
                q("Mutating webhook:",
                  "Modifica o recurso (ex.: injetar sidecar).",
                  ["Apenas valida.", "Apenas log.", "Apenas DNS."],
                  "Istio/Linkerd usam para injetar proxies. Vault Agent injetor também."),
                q("Gatekeeper baseia-se em:",
                  "OPA com CRDs ConstraintTemplate/Constraint.",
                  ["YAML estático.", "Bash.", "Shell."],
                  "ConstraintTemplate define a regra Rego; Constraint instancia com parâmetros."),
                q("Kyverno é:",
                  "Engine de policy nativa K8s sem precisar Rego.",
                  ["Substituto do kubectl.", "Apenas IPv6.", "Apenas Helm."],
                  "Políticas em YAML usam mesma sintaxe de manifests; curva mais rasa que Rego."),
                q("Admission protege contra:",
                  "Recursos que violem padrões antes de existir.",
                  ["Pods já criados.", "Apenas Service.", "Apenas etcd backup."],
                  "Pod já rodando precisa de runtime security (Falco/Tetragon)."),
                q("Modo audit:",
                  "Apenas registra violações sem bloquear.",
                  ["Bloqueia tudo.", "Apaga tudo.", "Substitui logs."],
                  "Use para mapear; avalie achados antes de partir para enforce."),
                q("ImagePolicyWebhook:",
                  "Controla quais imagens podem rodar no cluster.",
                  ["Substitui registry.", "Apenas DNS.", "Apenas IPv6."],
                  "Combinado com Cosign verifier, exige imagens assinadas."),
                q("Limite de admission:",
                  "Não enxerga problemas runtime, só no momento da admissão.",
                  ["Vê tudo sempre.", "Substitui monitoring.", "Substitui logs."],
                  "Pod aprovado pode comportar-se mal depois. Combine com runtime security."),
                q("Mutating + validating:",
                  "Comum em service mesh (sidecar injection + validações).",
                  ["São o mesmo recurso.", "Não convivem.", "Apenas em GKE."],
                  "Mutating roda primeiro, depois validating. Pode haver várias em série."),
                q("Falha em webhook:",
                  "Pode bloquear o cluster inteiro, configurar failurePolicy com cuidado.",
                  ["Sem efeito.", "Apenas warn.", "Acelera o cluster."],
                  "failurePolicy: Fail sem high-availability = cluster down quando webhook cai."),
            ],
        },
        # =====================================================================
        # 5.5 Zero Trust
        # =====================================================================
        {
            "title": "Zero Trust Architecture",
            "summary": "Modelo de 'nunca confiar, sempre verificar'.",
            "lesson": {
                "intro": (
                    "Perímetro (firewall castelo-fosso, VPN para entrar na 'rede segura') foi "
                    "o modelo de TI corporativa por décadas. Em arquiteturas modernas, multi-"
                    "cloud, dispositivos pessoais, SaaS, trabalho remoto, microsserviços, "
                    "isso quebrou. Zero Trust assume que <strong>o atacante já está dentro</strong> "
                    "e exige autenticação/autorização contínuas em cada acesso a cada recurso. "
                    "Não é uma ferramenta; é arquitetura. Pode levar anos para amadurecer."
                ),
                "body": (
                    "<h3>1. Por que perímetro falhou</h3>"
                    "<p>Modelo antigo:</p>"
                    "<ol>"
                    "<li>Funcionário entra na VPN.</li>"
                    "<li>Fica 'dentro da rede corporativa'.</li>"
                    "<li>Acessa file servers, banco de dados, sistemas internos.</li>"
                    "</ol>"
                    "<p>Problema: <strong>uma vez dentro, todo recurso é alcançável</strong>. "
                    "Notebook comprometido com malware? Atacante anda livre. Funcionário "
                    "demitido com credencial ativa? Mesma coisa. SQL Server interno sem patch? "
                    "Lateral movement sem fim.</p>"
                    "<p>Casos famosos:</p>"
                    "<ul>"
                    "<li><strong>Target (2013)</strong>: comprometimento de fornecedor de HVAC "
                    "deu acesso à rede interna; daí para POS, para 110M cartões.</li>"
                    "<li><strong>OPM (2015)</strong>: invasor permaneceu meses, exfiltrou 21M "
                    "registros de funcionários federais.</li>"
                    "<li><strong>SolarWinds (2020)</strong>: supply chain comprometida, malware "
                    "rodava 'dentro' em centenas de orgs.</li>"
                    "</ul>"
                    "<p>Em todos, perímetro 'segurou' mas atacante já estava do lado de dentro.</p>"

                    "<h3>2. Os pilares (NIST 800-207)</h3>"
                    "<ol>"
                    "<li><strong>Identidade forte</strong>: SSO + MFA forte (FIDO2 hardware "
                    "key &gt; TOTP &gt; SMS). Sem identidade verificada, nada mais importa.</li>"
                    "<li><strong>Device trust</strong>: dispositivo gerenciado, com disco "
                    "criptografado, patches em dia, EDR rodando, screen lock automático.</li>"
                    "<li><strong>Micro-segmentação</strong>: rede dividida em zonas pequenas; "
                    "comprometimento limitado em raio. Mesma ideia em K8s com NetworkPolicy.</li>"
                    "<li><strong>Autorização contínua</strong>: não basta autenticar uma vez; "
                    "decisões reavaliadas com base em contexto (localização, risco, recurso, "
                    "horário).</li>"
                    "<li><strong>Visibilidade</strong>: logs, traces, correlation centralizados. "
                    "Sem isso, não há como decidir o que é normal nem detectar anomalia.</li>"
                    "</ol>"

                    "<h3>3. NIST SP 800-207 em uma sentença</h3>"
                    "<p>'Zero Trust é uma coleção de conceitos e ideias projetadas para minimizar "
                    "incerteza ao tomar decisões de acesso accurate, least-privilege, por "
                    "request, em sistemas e serviços vistos como comprometidos.'</p>"
                    "<p>Note: <em>cada request</em>. Não cada sessão.</p>"

                    "<h3>4. Implementação prática para acesso humano</h3>"
                    "<p>Modelo BeyondCorp (Google) e ferramentas equivalentes:</p>"
                    "<pre><code>Engenheiro acessa app interna em https://app.corp.example.com\n"
                    "→ Cloudflare Access intercepta\n"
                    "→ Verifica identidade (SSO + MFA)\n"
                    "→ Verifica device posture (laptop gerenciado? OS atualizado? EDR?)\n"
                    "→ Avalia policy (grupo, recurso, horário, IP)\n"
                    "→ Concede ou nega\n"
                    "→ Se OK, proxy passa request com identidade injetada (header)\n"
                    "→ App interno confia no header (proxy é boundary)</code></pre>"
                    "<p>Sem VPN. Engenheiro de qualquer lugar acessa exatamente o que precisa, "
                    "nada mais. Cada acesso é decisão isolada.</p>"

                    "<h3>5. Implementação para serviço-a-serviço</h3>"
                    "<p>Microsserviços conversando: como provar identidade? Soluções:</p>"
                    "<ul>"
                    "<li><strong>Service Mesh</strong> (Istio, Linkerd, Consul): mTLS automático "
                    "+ identidade SPIFFE por carga. Pod 'web' fala com pod 'db' com cert mútuo.</li>"
                    "<li><strong>SPIFFE/SPIRE</strong>: padrão de identidade de carga. SVID "
                    "X.509 ou JWT.</li>"
                    "<li><strong>Workload Identity</strong> (cloud): pods recebem credencial "
                    "IAM via OIDC/IMDS sem secret estático.</li>"
                    "<li><strong>Tokens curtos JWT</strong> com aud/iss específicos.</li>"
                    "</ul>"

                    "<h3>6. Ferramentas comerciais e open-source</h3>"
                    "<ul>"
                    "<li><strong>Cloudflare Access</strong>: ZT corporativo SaaS.</li>"
                    "<li><strong>Tailscale</strong>: WireGuard mesh com identidade SSO. ZT "
                    "prático para times pequenos/médios.</li>"
                    "<li><strong>Twingate, Zscaler, Netskope, Palo Alto Prisma</strong>: "
                    "soluções enterprise.</li>"
                    "<li><strong>Pomerium, Boundary (HashiCorp)</strong>: ZT proxies open-source.</li>"
                    "<li><strong>Teleport</strong>: acesso a SSH, K8s, DB com identidade central.</li>"
                    "<li><strong>Service Mesh</strong>: Istio, Linkerd, Cilium Service Mesh.</li>"
                    "</ul>"

                    "<h3>7. Continuous authorization na prática</h3>"
                    "<p>Decisão única no login não basta. Reavalie:</p>"
                    "<ul>"
                    "<li>IP mudou drasticamente (Brasil → Romênia em 5min)? Risco alto.</li>"
                    "<li>Dispositivo perdeu compliance (patches expirados)? Bloqueie.</li>"
                    "<li>Tentativa de acesso a recurso sensível em horário incomum? MFA novo.</li>"
                    "<li>Comportamento atípico (download massivo)? Alerta + step-up.</li>"
                    "</ul>"
                    "<p>Essas decisões dependem de <em>signal collection</em>: SIEM, EDR, IdP "
                    "logs alimentando engine de decisão.</p>"

                    "<h3>8. Maturity model (CISA)</h3>"
                    "<p>5 pilares × 4 estágios:</p>"
                    "<ul>"
                    "<li><strong>Pilares</strong>: Identity, Devices, Networks, Applications, Data.</li>"
                    "<li><strong>Estágios</strong>: Traditional → Initial → Advanced → Optimal.</li>"
                    "</ul>"
                    "<p>Faça self-assessment. Identifique 2 pilares prioritários e 1 quick-win "
                    "por trimestre. Não tente fazer tudo de uma vez.</p>"

                    "<h3>9. Padrões e anti-padrões</h3>"
                    "<p><strong>Padrão</strong>: comece com aplicação interna nova → coloque "
                    "atrás de Access proxy → desligue acesso direto. Itere.</p>"
                    "<p><strong>Anti-padrão</strong>: 'comprar produto Zero Trust' como bala "
                    "de prata. Vendor diz 'aqui está sua ZT'. Sem mudança de processo, "
                    "arquitetura, cultura, é pintura nova em casa quebrada.</p>"

                    "<h3>10. Caminhos para começar</h3>"
                    "<ol>"
                    "<li><strong>Inventário</strong>: quais sistemas humanos acessam? Como?</li>"
                    "<li><strong>Identidade central</strong>: SSO + MFA forte para todos. Sem "
                    "isso, nada funciona.</li>"
                    "<li><strong>Device posture</strong>: política mínima (cripto, patches, "
                    "EDR, lock).</li>"
                    "<li><strong>Acesso a apps internas</strong>: substitua VPN para apps "
                    "internas por Access proxy. Comece com 1 app de baixo risco.</li>"
                    "<li><strong>Logging central</strong>: tudo manda log para SIEM.</li>"
                    "<li><strong>Service-to-service mTLS</strong>: service mesh nos clusters K8s.</li>"
                    "<li><strong>Continuous evaluation</strong>: integre signals de risco.</li>"
                    "</ol>"

                    "<h3>11. ZT em K8s</h3>"
                    "<ul>"
                    "<li>RBAC granular (5.2).</li>"
                    "<li>NetworkPolicy default-deny (5.3).</li>"
                    "<li>mTLS via service mesh.</li>"
                    "<li>Admission policies (5.4).</li>"
                    "<li>Audit log → SIEM.</li>"
                    "<li>Imagens assinadas + SBOM.</li>"
                    "</ul>"
                    "<p>Cada camada limita o blast radius da próxima falha.</p>"

                    "<h3>12. Limites e críticas</h3>"
                    "<ul>"
                    "<li>Tudo depende de identidade, comprometeu IdP, comprometeu tudo. "
                    "Logo: hardening do IdP é missão crítica.</li>"
                    "<li>Latência adicional em cada acesso (proxy + decisão).</li>"
                    "<li>Custo de implementação alto inicialmente.</li>"
                    "<li>Funcionalidade legada nem sempre suporta (apps antigos sem header "
                    "auth).</li>"
                    "<li>Nem tudo precisa de ZT (impressora ofício 3 anos pelo menos não, "
                    "priorize por risco).</li>"
                    "</ul>"
                ),
                "practical": (
                    "Defina device posture mínima (disco criptografado, MFA hardware key, OS "
                    "atualizado, EDR rodando). Configure Cloudflare Access (ou Tailscale, ou "
                    "Pomerium) para que uma ferramenta interna (ex.: Grafana, ArgoCD) só seja "
                    "acessível a dispositivos que cumpram a posture. Verifique a trilha de "
                    "auditoria de quem acessou o que e quando."
                ),
            },
            "materials": [
                m("NIST 800-207 Zero Trust", "https://csrc.nist.gov/publications/detail/sp/800-207/final", "docs", ""),
                m("Google BeyondCorp", "https://cloud.google.com/beyondcorp", "article", ""),
                m("Cloudflare: Zero Trust", "https://www.cloudflare.com/learning/access-management/what-is-zero-trust/", "article", ""),
                m("CISA Zero Trust Maturity Model", "https://www.cisa.gov/zero-trust-maturity-model", "docs", ""),
                m("Tailscale", "https://tailscale.com/kb", "tool", ""),
                m("SPIFFE/SPIRE", "https://spiffe.io/docs/latest/", "docs", "Identidade para workloads."),
                m("Teleport", "https://goteleport.com/docs/", "tool", "ZT acesso para SSH/K8s/DB."),
            ],
            "questions": [
                q("Zero Trust premissa:",
                  "Não há rede confiável, sempre autenticar/autorizar.",
                  ["A rede interna é segura.", "Firewall basta.", "Senha forte é suficiente."],
                  "Assume invasor já dentro. Cada recurso = nova decisão de acesso."),
                q("BeyondCorp do Google é:",
                  "Implementação prática de zero trust corporativo.",
                  ["Tipo de DNS.", "Cluster K8s.", "Apenas SSO."],
                  "Pioneiro: sem VPN, todo acesso via proxy + identidade + device + contexto."),
                q("Micro-segmentação:",
                  "Reduz blast radius, atacante não anda pela rede livremente.",
                  ["Aumenta latência sempre.", "Substitui IAM.", "Apenas para web."],
                  "Em K8s: NetworkPolicy + service mesh. Em rede: VLANs / ZTNA."),
                q("Device posture:",
                  "Avalia se o dispositivo cumpre requisitos antes de acessar.",
                  ["Apenas IP.", "Apenas usuário.", "Sempre permite."],
                  "Disco cripto, OS atualizado, EDR rodando. Política checa no acesso."),
                q("Service mesh ajuda em:",
                  "mTLS, AuthZ, observabilidade entre serviços.",
                  ["Apenas cache.", "Substitui ingress.", "Apenas DNS."],
                  "Istio/Linkerd configuram identidade por pod e cifram tráfego entre pods automaticamente."),
                q("VPN tradicional vs Zero Trust:",
                  "VPN dá acesso amplo; ZT autoriza por recurso.",
                  ["São idênticos.", "ZT é menos seguro.", "VPN é mais granular."],
                  "VPN é 'tudo ou nada'. ZT autoriza por recurso e em cada acesso."),
                q("Identidade forte exige:",
                  "MFA + sinal de risco contextual.",
                  ["Apenas senha.", "Apenas IP estático.", "SMS sempre."],
                  "FIDO2/WebAuthn é estado da arte. SMS é forma fraca (SIM swap)."),
                q("Tailscale baseado em:",
                  "WireGuard com identidade/SSO.",
                  ["IPSec puro.", "L2TP.", "PPTP."],
                  "Mesh privado entre dispositivos com identidade humana via OIDC. Bom ZT prático."),
                q("Continuous authorization:",
                  "Reavalia decisões durante a sessão.",
                  ["Apenas no login.", "Apenas no logout.", "Manualmente."],
                  "Risco mudou (novo IP, dispositivo perdeu compliance)? Sessão é encerrada/elevada."),
                q("ZT NÃO é:",
                  "Apenas comprar uma ferramenta.",
                  ["Filosofia + arquitetura.", "Modelo gradual.", "Suportado por padrões NIST."],
                  "Vendors vendem 'ZT in a box'. Real ZT exige mudança de processos e arquitetura."),
            ],
        },
        # =====================================================================
        # 5.6 Runtime Security
        # =====================================================================
        {
            "title": "Runtime Security",
            "summary": "Detectar se alguém invadiu um container em execução.",
            "lesson": {
                "intro": (
                    "Você fez SAST, SCA, scan de imagem, hardening de pod, NetworkPolicy, "
                    "admission control, e mesmo assim algo estranho está rodando agora "
                    "naquele pod. Atacante explorou um zero-day, supply chain comprometida, "
                    "credencial vazou em log. Runtime security é a camada que detecta "
                    "atividade anômala em <em>execução</em>, 'EDR para containers'. Sem "
                    "ela, você só descobre o incidente quando o blog post sai."
                ),
                "body": (
                    "<h3>1. eBPF: a base moderna</h3>"
                    "<p>Antes do eBPF, monitorar comportamento de processos exigia LKMs "
                    "(módulos de kernel) ou ptrace, soluções pesadas, frágeis ou inseguras. "
                    "<strong>eBPF</strong> (extended Berkeley Packet Filter) permite carregar "
                    "programas pequenos, verificados estaticamente, no kernel Linux, com baixo "
                    "overhead. Você anexa um programa eBPF a um syscall, kprobe, tracepoint, "
                    "evento de rede, e ele observa/age sem recompilar kernel.</p>"
                    "<p>Por que isso importa para segurança:</p>"
                    "<ul>"
                    "<li>Visibilidade granular (cada syscall, cada conexão).</li>"
                    "<li>Sem reboot, sem patch de kernel.</li>"
                    "<li>Verificador garante que não trava o sistema.</li>"
                    "<li>Mesma técnica usada por observabilidade (Pixie), networking (Cilium), "
                    "security (Falco, Tetragon).</li>"
                    "</ul>"

                    "<h3>2. Falco: o padrão CNCF</h3>"
                    "<p>Falco lê eventos do kernel via eBPF (ou módulo) e avalia contra regras "
                    "YAML. DaemonSet em K8s; alertas via stdout, syslog, ou Falcosidekick "
                    "(que roteia para Slack, PagerDuty, SIEM).</p>"
                    "<p>Exemplos de regras default:</p>"
                    "<ul>"
                    "<li><strong>Terminal shell in container</strong>: alguém fez "
                    "<code>kubectl exec</code> e abriu shell.</li>"
                    "<li><strong>Write below etc</strong>: processo escreveu em "
                    "<code>/etc/...</code> dentro do container.</li>"
                    "<li><strong>Outbound connection to suspicious IP</strong>: pod fez "
                    "conexão para IP em listas de threat intel.</li>"
                    "<li><strong>Privilege escalation attempt</strong>: setuid binary executado.</li>"
                    "<li><strong>Read sensitive file</strong>: leitura de "
                    "<code>/etc/shadow</code>, <code>/proc/self/maps</code>.</li>"
                    "<li><strong>Container drift detected</strong>: binário novo apareceu "
                    "(não estava na imagem).</li>"
                    "</ul>"
                    "<pre><code># exemplo de regra Falco\n"
                    "- rule: Shell in container\n"
                    "  desc: Detecta shell em container de produção\n"
                    "  condition: >\n"
                    "    container and shell_procs and proc.tty != 0\n"
                    "    and not proc.pname in (allowed_shell_parent_processes)\n"
                    "    and k8s.ns.name in (production_ns)\n"
                    "  output: >\n"
                    "    Shell em pod prod (user=%user.name shell=%proc.name\n"
                    "    pod=%k8s.pod.name ns=%k8s.ns.name image=%container.image.repository)\n"
                    "  priority: WARNING\n"
                    "  tags: [container, shell, mitre_execution]</code></pre>"

                    "<h3>3. Tetragon (Cilium)</h3>"
                    "<p>Da Cilium. Diferencial: <strong>ações em kernel</strong>, pode kill "
                    "processo ou bloquear syscall imediatamente, não só alertar. Usa Tracing "
                    "Policies em CRDs:</p>"
                    "<pre><code>apiVersion: cilium.io/v1alpha1\n"
                    "kind: TracingPolicy\n"
                    "metadata: { name: block-curl-in-pods }\n"
                    "spec:\n"
                    "  kprobes:\n"
                    "  - call: \"sys_execve\"\n"
                    "    syscall: true\n"
                    "    args:\n"
                    "    - index: 0\n"
                    "      type: \"string\"\n"
                    "    selectors:\n"
                    "    - matchArgs:\n"
                    "      - index: 0\n"
                    "        operator: \"Postfix\"\n"
                    "        values: [\"/curl\", \"/wget\"]\n"
                    "      matchActions:\n"
                    "      - action: Sigkill   # mata o processo</code></pre>"
                    "<p>Útil para resposta automática a comportamento de exfiltração. Mas "
                    "tenha cuidado: ações em kernel são definitivas.</p>"

                    "<h3>4. Tracee, Cilium Tetragon, Sysdig</h3>"
                    "<ul>"
                    "<li><strong>Tracee</strong> (Aqua): tracing eBPF, foco em forensics.</li>"
                    "<li><strong>Sysdig Secure</strong>: comercial, integra runtime + image scan + "
                    "compliance.</li>"
                    "<li><strong>Pixie</strong>: observabilidade eBPF (não foca segurança, mas "
                    "complementa).</li>"
                    "</ul>"

                    "<h3>5. MITRE ATT&amp;CK Containers</h3>"
                    "<p>Matriz de táticas/técnicas usadas por adversários contra containers. "
                    "Categorias principais:</p>"
                    "<ul>"
                    "<li><strong>Initial Access</strong>: app vulnerável, image maliciosa.</li>"
                    "<li><strong>Execution</strong>: kubectl exec, container escape.</li>"
                    "<li><strong>Persistence</strong>: cronjob malicioso, sidecar injection.</li>"
                    "<li><strong>Privilege Escalation</strong>: capability abuse, setuid.</li>"
                    "<li><strong>Defense Evasion</strong>: desligar logging, esconder processos.</li>"
                    "<li><strong>Credential Access</strong>: ler ServiceAccount token.</li>"
                    "<li><strong>Discovery</strong>: listar pods, services, configs.</li>"
                    "<li><strong>Lateral Movement</strong>: explorar pod vizinho via API.</li>"
                    "<li><strong>Impact</strong>: ransomware, mineração, exfil.</li>"
                    "</ul>"
                    "<p>Use para mapear cobertura: 'Falco detecta T1059 (Command and Scripting "
                    "Interpreter)? T1611 (Escape to Host)? T1552 (Unsecured Credentials)?'. "
                    "Lacunas viram regras novas.</p>"

                    "<h3>6. Operação no dia a dia</h3>"
                    "<ul>"
                    "<li>Comece com regras default. Por 2 semanas, monitore volume e qualidade "
                    "dos alertas.</li>"
                    "<li>Tune falsos positivos: pods de debug com shell legítimo, "
                    "writes esperados, etc. Use labels para excluir.</li>"
                    "<li>Crie regras customizadas para seu domínio (ex.: 'pod do PCI namespace "
                    "nunca deveria fazer egress para IP externo').</li>"
                    "<li>Runbook por severidade. Alertas críticos com SLA &lt; 15 min.</li>"
                    "<li>Integre com SOAR para resposta inicial automática (isolar pod, "
                    "snapshot).</li>"
                    "<li>Game days regulares testando detecção (ver 5.8).</li>"
                    "</ul>"

                    "<h3>7. Resposta a incidente runtime</h3>"
                    "<p>Alerta de alta severidade (ex.: privilege escalation):</p>"
                    "<ol>"
                    "<li><strong>Confirmar</strong>: é falso positivo? Olhe contexto, host, "
                    "imagem, evento.</li>"
                    "<li><strong>Conter</strong>: aplique NP <code>egress=none</code> e "
                    "<code>ingress=none</code> no pod (label seletora). Mas <em>não</em> "
                    "delete o pod ainda.</li>"
                    "<li><strong>Forensics</strong>: snapshot do filesystem do pod (kubectl cp, "
                    "ou debug ephemeral container), captura de syscalls/conexões.</li>"
                    "<li><strong>Isolar node</strong> se necessário: cordon + drain (cuidado "
                    "para não evict para outro node sem isolar antes).</li>"
                    "<li><strong>Notificar</strong> Incident Commander e iniciar runbook IR.</li>"
                    "<li><strong>Erradicar</strong>: rebuild da imagem, rotacionar credenciais, "
                    "redeploy de tudo no namespace afetado.</li>"
                    "<li><strong>Postmortem</strong>: como passou? Lacuna em prevenção, "
                    "detecção, resposta?</li>"
                    "</ol>"

                    "<h3>8. Limites de runtime security</h3>"
                    "<ul>"
                    "<li>É <strong>detecção</strong>, não prevenção. Atacante já está dentro.</li>"
                    "<li>Falsos positivos consomem time de SOC.</li>"
                    "<li>Falsos negativos: ataque sofisticado pode evadir regras conhecidas.</li>"
                    "<li>Overhead de eBPF é baixo, mas não-zero (especialmente em workloads "
                    "I/O-intensivos).</li>"
                    "<li>Regras precisam manutenção contínua à medida que apps mudam.</li>"
                    "</ul>"
                    "<p>Use junto com prevenção (admission, NP, RBAC, securityContext), "
                    "defesa em profundidade.</p>"

                    "<h3>9. Escolhendo a ferramenta</h3>"
                    "<ul>"
                    "<li><strong>Open-source, K8s-first</strong>: Falco (mais maduro), "
                    "Tetragon (ações em kernel).</li>"
                    "<li><strong>Comercial</strong>: Sysdig Secure, Aqua, Crowdstrike "
                    "Falcon (containers).</li>"
                    "<li><strong>Cloud-native managed</strong>: AWS GuardDuty for EKS, GCP "
                    "Container Threat Detection.</li>"
                    "</ul>"
                    "<p>Combine. GuardDuty for EKS detecta padrões em logs do CloudTrail/VPC; "
                    "Falco no node detecta syscalls. Visões diferentes, complementares.</p>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Falco instalado, alertas ignorados</strong>: tool ruidosa "
                    "vira spam → silêncio. Tune!</li>"
                    "<li><strong>Sem runbook</strong>: alerta dispara, ninguém sabe responder.</li>"
                    "<li><strong>Apenas regras default</strong>: contexto do seu domínio "
                    "exige customização.</li>"
                    "<li><strong>Runtime security como única camada</strong>: detecta tarde; "
                    "combine com prevenção.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Instale Falco via Helm. Faça <code>kubectl exec -it &lt;pod&gt; -- bash</code> "
                    "em um pod e veja o alerta 'Terminal shell in container' nos logs do Falco. "
                    "Tune a regra para ignorar pods com label <code>debug=true</code> mas mantenha "
                    "alerta para pods sem essa label. Em seguida, configure Falcosidekick para "
                    "enviar alertas para um webhook simples (httpbin.org) e simule um evento "
                    "high-severity."
                ),
            },
            "materials": [
                m("Falco", "https://falco.org/docs/", "docs", ""),
                m("Tetragon", "https://tetragon.io/docs/", "docs", ""),
                m("Sysdig: Container security", "https://sysdig.com/learn-cloud-native/", "article", ""),
                m("eBPF.io", "https://ebpf.io/", "docs", ""),
                m("MITRE ATT&CK Containers", "https://attack.mitre.org/matrices/enterprise/containers/", "docs", ""),
                m("Falcosidekick", "https://github.com/falcosecurity/falcosidekick", "tool", "Roteia alertas Falco."),
                m("Tracee", "https://aquasecurity.github.io/tracee/latest/", "tool", "Forensics + runtime."),
            ],
            "questions": [
                q("Falco detecta:",
                  "Comportamentos suspeitos via syscalls/eBPF.",
                  ["Vulnerabilidades estáticas.", "Apenas DNS.", "Apenas ICMP."],
                  "Como antivírus comportamental para containers. Detecta ações, não assinaturas estáticas."),
                q("eBPF permite:",
                  "Programas seguros no kernel sem modificar fonte.",
                  ["Recompilar kernel.", "Apenas em macOS.", "Apenas como root."],
                  "Verificador estático garante que o programa não trava o kernel. Revolução em observability."),
                q("Detecção runtime complementa:",
                  "Controles preventivos (SAST, SCA, admission).",
                  ["Substitui tudo.", "Substitui logs.", "Reduz IAM."],
                  "Defesa em camadas: prevenir + detectar + responder."),
                q("Shell em pod produção é:",
                  "Sinal a investigar, geralmente anomalia.",
                  ["Boa prática.", "Comum em prod.", "Necessário."],
                  "Em prod imutável, kubectl exec é exceção. Auditoria mostra quem e quando."),
                q("Tetragon difere de Falco:",
                  "Tetragon tem ações ativas (kill) em kernel.",
                  ["São idênticos.", "Tetragon não tem regras.", "Falco é apenas Java."],
                  "Falco alerta; Tetragon pode bloquear/kill imediatamente."),
                q("MITRE ATT&CK:",
                  "Knowledge base de táticas/técnicas de adversários.",
                  ["IDE.", "Cluster.", "Compiler."],
                  "Use para mapear regras Falco/Tetragon e medir cobertura defensiva."),
                q("Sidecar de monitoramento:",
                  "Pode aumentar overhead, escolha modo eBPF/host quando possível.",
                  ["Sem overhead.", "Sempre obrigatório.", "Apenas em DaemonSet."],
                  "DaemonSet com eBPF tem footprint menor que sidecar por pod."),
                q("Falsos positivos:",
                  "Devem ser tunados via regras customizadas.",
                  ["Sempre ignorar.", "Sempre desativar.", "Substituir tool."],
                  "Cada ambiente tem padrões diferentes. Tuning é trabalho contínuo."),
                q("Resposta a alerta runtime:",
                  "Runbook claro com escala e isolamento.",
                  ["Reiniciar tudo.", "Ignorar.", "Apagar logs."],
                  "Snapshot do pod (forensics), isolar (NP), notificar IR. Não delete sem evidência."),
                q("Observabilidade runtime:",
                  "Dá visão 'em vivo' do que cluster faz.",
                  ["Substitui métricas.", "Apenas debug.", "Não funciona em prod."],
                  "Hubble/Pixie mostram execuções/conexões em tempo real, útil em incidente."),
            ],
        },
        # =====================================================================
        # 5.7 Observabilidade Avançada
        # =====================================================================
        {
            "title": "Observabilidade Avançada",
            "summary": "Rastrear o caminho de uma requisição entre sistemas.",
            "lesson": {
                "intro": (
                    "Métricas dizem 'o quê' (CPU 80%, latência p99 1s); logs dizem 'o que "
                    "aconteceu' (exception em handler); traces dizem 'por onde foi' (login → "
                    "auth → DB → cache → email). Em arquitetura distribuída com 30+ "
                    "microsserviços, sem traces você investiga incidentes às cegas. "
                    "Observabilidade avançada é dominar os três pilares, e correlacioná-los."
                ),
                "body": (
                    "<h3>1. Os três pilares</h3>"
                    "<ul>"
                    "<li><strong>Metrics</strong>: séries temporais de números agregados. "
                    "'reqs/s', 'erro 500/s', 'CPU%'. Baixo custo, alto poder estatístico, baixa "
                    "cardinalidade. Usado em dashboards e alertas.</li>"
                    "<li><strong>Logs</strong>: eventos textuais discretos. 'login failed for "
                    "user@x'. Alto detalhe, alto custo de armazenamento, busca por strings.</li>"
                    "<li><strong>Traces</strong>: árvore de spans representando o caminho de "
                    "uma requisição entre serviços. Cada span tem início/fim, atributos, "
                    "status. Permite ver onde tempo foi gasto, onde falhou.</li>"
                    "</ul>"
                    "<p>Cada um responde perguntas diferentes. Os três <em>juntos</em>, com "
                    "correlation, permitem raciocínio rápido em incidente.</p>"

                    "<h3>2. Tracing 101</h3>"
                    "<p>Uma requisição vira um <strong>trace</strong>; cada operação dentro "
                    "vira um <strong>span</strong>. Spans formam árvore com pai/filho:</p>"
                    "<pre><code>POST /checkout                              [800ms]\n"
                    "├── auth.verify_token                       [10ms]\n"
                    "├── inventory.check_stock                   [30ms]\n"
                    "├── payment.charge                          [600ms]\n"
                    "│   ├── stripe.create_charge                [580ms]\n"
                    "│   └── db.write_charge                     [15ms]\n"
                    "├── notification.send_email                 [40ms]\n"
                    "└── db.write_order                          [20ms]</code></pre>"
                    "<p>Cada span tem:</p>"
                    "<ul>"
                    "<li><code>trace_id</code>: identificador único do trace.</li>"
                    "<li><code>span_id</code>: identificador do span.</li>"
                    "<li><code>parent_span_id</code>: span pai.</li>"
                    "<li>start/end timestamps.</li>"
                    "<li>service.name, operation.name.</li>"
                    "<li>status (ok/error).</li>"
                    "<li>attributes (http.method, db.statement, user.id, etc.).</li>"
                    "<li>events (logs locais ao span).</li>"
                    "</ul>"
                    "<p>Propagação via headers HTTP, padrão W3C TraceContext:</p>"
                    "<pre><code>traceparent: 00-{trace-id-32-hex}-{parent-id-16-hex}-{flags-2-hex}\n"
                    "tracestate: rojo=00f067aa0ba902b7</code></pre>"

                    "<h3>3. OpenTelemetry: o padrão</h3>"
                    "<p>OTel é projeto CNCF que padroniza coleta de métricas, logs e traces. "
                    "Componentes:</p>"
                    "<ul>"
                    "<li><strong>SDK</strong> em cada linguagem: instrumenta código.</li>"
                    "<li><strong>Auto-instrumentação</strong>: para muitas libs (HTTP, DB, RPC) "
                    "sem mudar código.</li>"
                    "<li><strong>OTLP</strong>: protocolo binário (gRPC ou HTTP) entre app e "
                    "coletor.</li>"
                    "<li><strong>Collector</strong>: agente que recebe OTLP/Jaeger/Zipkin/"
                    "Prometheus, processa, exporta para backend.</li>"
                    "</ul>"
                    "<pre><code># Python\n"
                    "$ pip install opentelemetry-distro opentelemetry-exporter-otlp\n"
                    "$ opentelemetry-bootstrap --action=install\n"
                    "$ OTEL_SERVICE_NAME=checkout \\\n"
                    "  OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \\\n"
                    "  opentelemetry-instrument python app.py\n"
                    "# pronto: traces para HTTP, requests, sqlalchemy, redis... aparecem no backend</code></pre>"

                    "<h3>4. Backends de traces</h3>"
                    "<ul>"
                    "<li><strong>Jaeger</strong>: clássico CNCF, Cassandra/Elasticsearch como storage.</li>"
                    "<li><strong>Tempo</strong> (Grafana): backend baseado em S3/GCS, barato.</li>"
                    "<li><strong>Zipkin</strong>: pioneiro Twitter, ainda usado.</li>"
                    "<li><strong>Honeycomb</strong>: SaaS focado em high-cardinality, query "
                    "interativa potente.</li>"
                    "<li><strong>Datadog APM, New Relic, Dynatrace</strong>: SaaS comerciais "
                    "completos.</li>"
                    "<li><strong>SigNoz, Uptrace</strong>: open-source self-hosted.</li>"
                    "</ul>"

                    "<h3>5. Métricas: além das médias</h3>"
                    "<p>Trabalhe com <strong>histogramas</strong>, não médias. p50/p95/p99 "
                    "dizem onde mora a dor:</p>"
                    "<pre><code>avg_latency = 100ms                    # parece bom\n"
                    "p50 = 50ms\n"
                    "p99 = 5s                                # 1% dos usuários: experiência terrível</code></pre>"
                    "<p>Estrutura mental para serviços (Tom Wilkie): <strong>RED</strong>:</p>"
                    "<ul>"
                    "<li><strong>Rate</strong>: reqs/s.</li>"
                    "<li><strong>Errors</strong>: erro/s.</li>"
                    "<li><strong>Duration</strong>: distribuição de latência.</li>"
                    "</ul>"
                    "<p>Para recursos (Brendan Gregg): <strong>USE</strong>:</p>"
                    "<ul>"
                    "<li><strong>Utilization</strong>: % de uso.</li>"
                    "<li><strong>Saturation</strong>: fila de espera.</li>"
                    "<li><strong>Errors</strong>: erros do recurso.</li>"
                    "</ul>"
                    "<p>Google SRE: <strong>4 Golden Signals</strong>: latency, traffic, errors, "
                    "saturation.</p>"

                    "<h3>6. Cardinalidade: a armadilha</h3>"
                    "<p>Cardinalidade é o número de séries únicas em uma métrica. Cada "
                    "combinação distinta de labels = série nova.</p>"
                    "<pre><code># RUIM\n"
                    "http_requests_total{user_id=\"123\", path=\"/api/users/456\"}\n"
                    "# 1M users * 100k paths = 100B séries → quebra Prometheus\n"
                    "\n"
                    "# BOM\n"
                    "http_requests_total{route=\"/api/users/:id\", method=\"GET\", status=\"200\"}\n"
                    "# poucas séries, alta utilidade</code></pre>"
                    "<p>Detalhes de alta cardinalidade vão para traces e logs (que <em>são</em> "
                    "high-cardinality por design). Prometheus/cortex/mimir não suportam.</p>"

                    "<h3>7. Sampling em traces</h3>"
                    "<p>Coletar 100% dos traces custa armazenamento. Estratégias:</p>"
                    "<ul>"
                    "<li><strong>Head-based</strong>: decisão na primeira chamada (random N%). "
                    "Simples; perde casos raros.</li>"
                    "<li><strong>Tail-based</strong>: coleta tudo, decide depois com base em "
                    "atributos do trace completo (priorizar erros, lentos). Mais caro de operar; "
                    "exige collector com buffer.</li>"
                    "<li><strong>Probabilistic</strong>: 1% de tudo.</li>"
                    "<li><strong>Rate-limiting</strong>: máx N traces/s por serviço.</li>"
                    "</ul>"
                    "<pre><code># OTel Collector tail sampling\n"
                    "processors:\n"
                    "  tail_sampling:\n"
                    "    decision_wait: 30s\n"
                    "    policies:\n"
                    "    - name: errors-policy\n"
                    "      type: status_code\n"
                    "      status_code: { status_codes: [ERROR] }\n"
                    "    - name: slow-policy\n"
                    "      type: latency\n"
                    "      latency: { threshold_ms: 1000 }\n"
                    "    - name: random-policy\n"
                    "      type: probabilistic\n"
                    "      probabilistic: { sampling_percentage: 1 }</code></pre>"

                    "<h3>8. Correlation entre logs, métricas e traces</h3>"
                    "<p>Inclua <code>trace_id</code> em cada log:</p>"
                    "<pre><code>{\"timestamp\": \"...\", \"level\": \"ERROR\",\n"
                    " \"service\": \"payment\", \"trace_id\": \"4bf92f3577b34da6\",\n"
                    " \"span_id\": \"00f067aa0ba902b7\",\n"
                    " \"msg\": \"stripe charge failed\", \"user_id\": \"u-123\"}</code></pre>"
                    "<p>No Grafana com Loki + Tempo + Prometheus:</p>"
                    "<ol>"
                    "<li>Você vê pico de erros em métrica (Prometheus).</li>"
                    "<li>Drill-down em logs do serviço (Loki).</li>"
                    "<li>Click em trace_id de um log com erro → vai direto para o trace (Tempo).</li>"
                    "<li>No trace, vê qual span falhou e quanto tempo gastou onde.</li>"
                    "</ol>"
                    "<p>Sem correlation, você fica fazendo correlation manual, impossível "
                    "em escala.</p>"

                    "<h3>9. SLI / SLO / Error Budget</h3>"
                    "<ul>"
                    "<li><strong>SLI</strong> (Service Level Indicator): métrica que mede "
                    "experiência do usuário. Ex.: '% de requests &lt; 500ms'.</li>"
                    "<li><strong>SLO</strong> (Objective): meta numérica. Ex.: '99.9% das requests "
                    "&lt; 500ms em janela de 30 dias'.</li>"
                    "<li><strong>Error Budget</strong>: 100% - SLO. Para 99.9% = 43 min/mês "
                    "de erro permitido. Quando o budget queima rápido, freie deploys.</li>"
                    "<li><strong>SLA</strong>: contrato com cliente. Geralmente mais frouxo que "
                    "SLO interno (você quer detectar antes de violar contrato).</li>"
                    "</ul>"

                    "<h3>10. Alerting eficaz</h3>"
                    "<ul>"
                    "<li>Alerta deve ser <strong>actionable</strong>: alguém precisa fazer algo "
                    "agora. Senão, vira ruído.</li>"
                    "<li>Alerte em SLI/SLO, não em causas (CPU alto não é necessariamente "
                    "incidente; latência percebida é).</li>"
                    "<li>Multi-window multi-burn-rate (Google SRE Workbook): alerte rápido para "
                    "queimadas grandes, devagar para pequenas.</li>"
                    "<li>Cada alerta tem runbook em URL: 'o que fazer ao receber'.</li>"
                    "</ul>"

                    "<h3>11. Pipeline completo: coletor + backend</h3>"
                    "<pre><code># otel-collector-config.yaml\n"
                    "receivers:\n"
                    "  otlp:\n"
                    "    protocols:\n"
                    "      grpc: {}\n"
                    "      http: {}\n"
                    "  prometheus:\n"
                    "    config:\n"
                    "      scrape_configs:\n"
                    "      - job_name: app\n"
                    "        kubernetes_sd_configs: [{role: pod}]\n"
                    "\n"
                    "processors:\n"
                    "  batch: {}\n"
                    "  resource:\n"
                    "    attributes:\n"
                    "    - key: env\n"
                    "      value: prod\n"
                    "      action: insert\n"
                    "  tail_sampling: { ... }\n"
                    "\n"
                    "exporters:\n"
                    "  otlp/tempo: { endpoint: tempo:4317 }\n"
                    "  prometheus/mimir: { endpoint: 0.0.0.0:9090 }\n"
                    "  loki: { endpoint: http://loki:3100/loki/api/v1/push }\n"
                    "\n"
                    "service:\n"
                    "  pipelines:\n"
                    "    traces: { receivers: [otlp], processors: [batch, tail_sampling], exporters: [otlp/tempo] }\n"
                    "    metrics: { receivers: [otlp, prometheus], processors: [batch, resource], exporters: [prometheus/mimir] }\n"
                    "    logs: { receivers: [otlp], processors: [batch], exporters: [loki] }</code></pre>"

                    "<h3>12. Service Map automático</h3>"
                    "<p>De traces, ferramentas geram mapa de dependências do sistema: 'web "
                    "chama auth e api; api chama postgres e redis'. Indispensável em "
                    "incidentes ('auth está lento → todos os clientes downstream sofrem'). "
                    "Disponível em Datadog, Honeycomb, Grafana Tempo, Jaeger.</p>"

                    "<h3>13. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Logs e métricas em silos sem correlation</strong>: investigação "
                    "vira detetive cego.</li>"
                    "<li><strong>Cardinalidade explosiva em métricas</strong>: derruba Prometheus.</li>"
                    "<li><strong>100% sampling sem necessidade</strong>: storage caríssimo.</li>"
                    "<li><strong>Alertas em causas, não sintomas</strong>: pager toca por nada "
                    "ou nunca toca quando precisa.</li>"
                    "<li><strong>Sem runbook por alerta</strong>: oncall acordado às 3am com "
                    "'CPU alto' e zero contexto.</li>"
                    "<li><strong>Trace só em alguns serviços</strong>: lacunas escondem o "
                    "problema.</li>"
                    "<li><strong>Sem instrumentação custom</strong>: auto-instrumentação capta "
                    "HTTP, mas perde lógica de negócio.</li>"
                    "</ul>"

                    "<h3>14. Custo</h3>"
                    "<ul>"
                    "<li>Storage de logs cresce linear com tráfego, retenção curta "
                    "(7-30 dias 'quente', tier frio para arquivo).</li>"
                    "<li>Métricas: cardinalidade controlada → custo controlado.</li>"
                    "<li>Traces: sampling agressivo + tail-based para preservar erros.</li>"
                    "<li>Vendor SaaS pode ficar caríssimo, calcule por GB ingerido + "
                    "host monitorado.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Instrumente uma app Python com <code>opentelemetry-instrument python "
                    "app.py</code>. Configure exportador OTLP para Grafana Tempo. Faça uma "
                    "request que passe por 3 microserviços (use docker-compose). No Grafana, "
                    "navegue do log com erro → trace_id → span tree e identifique o gargalo de "
                    "latência. Configure alerta em p99 &gt; 1s queimando error budget de 99.9% SLO."
                ),
            },
            "materials": [
                m("OpenTelemetry", "https://opentelemetry.io/docs/", "docs", ""),
                m("Distributed Systems Observability (livro)", "https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/", "book", ""),
                m("Honeycomb: Tracing 101", "https://www.honeycomb.io/blog/tracing-101", "article", ""),
                m("Grafana Tempo", "https://grafana.com/docs/tempo/latest/", "docs", ""),
                m("Jaeger", "https://www.jaegertracing.io/docs/latest/", "docs", ""),
                m("W3C TraceContext", "https://www.w3.org/TR/trace-context/", "docs", "Padrão de propagação de trace_id."),
                m("Google SRE Workbook", "https://sre.google/workbook/table-of-contents/", "book", "Alerting e SLOs."),
            ],
            "questions": [
                q("Trace é:",
                  "Conjunto de spans que representa caminho de uma requisição.",
                  ["Linha de log.", "Métrica de uptime.", "Apenas DNS."],
                  "Cada span é uma operação; juntos formam árvore. Permite ver onde tempo é gasto."),
                q("OpenTelemetry padroniza:",
                  "Coleta de métricas, logs e traces.",
                  ["Apenas métricas.", "Apenas logs.", "Apenas Java."],
                  "SDK + protocolo OTLP. Backend pode ser trocado sem mudar instrumentação."),
                q("Span attributes:",
                  "Tags que enriquecem contexto (route, user, db).",
                  ["Bug.", "Tipo de cripto.", "Nome de container."],
                  "Use atributos semânticos padronizados (HTTP, DB, RPC) para queries consistentes."),
                q("p99 vs avg:",
                  "p99 mostra cauda, onde mora a dor de muitos usuários.",
                  ["Avg é melhor sempre.", "São idênticos.", "p99 não importa."],
                  "Média de 100ms com p99 de 5s = 1% dos usuários têm experiência terrível."),
                q("Sampling em traces:",
                  "Reduz custo coletando subconjunto representativo.",
                  ["Ignora todos.", "Aumenta custo.", "Substitui métricas."],
                  "Tail-based prioriza erros e slow paths. Head-based é mais simples."),
                q("Correlation entre logs e traces:",
                  "Use o trace_id em campos do log.",
                  ["Não é possível.", "Substitui IAM.", "Apenas DNS."],
                  "Loki + Tempo + Prometheus conseguem 'pular' entre os três por trace_id."),
                q("Service map:",
                  "Visão das dependências entre serviços (a partir de traces).",
                  ["Mapa físico do datacenter.", "Apenas Cypher.", "Tipo de TLS."],
                  "Datadog/Tempo/Jaeger geram automaticamente. Em incidente: 'qual serviço chama qual'."),
                q("RED method:",
                  "Rate, Errors, Duration, métricas para serviços.",
                  ["Backup.", "Cache.", "Apenas DNS."],
                  "Por endpoint. Combina com USE para visão completa."),
                q("Cardinalidade alta:",
                  "Pode quebrar backends de métricas.",
                  ["Não importa.", "Reduz custo.", "Acelera consulta."],
                  "Cada combinação única de labels = série. user_id em métrica = milhões de séries."),
                q("OTel Collector:",
                  "Pipeline configurável de receivers/processors/exporters.",
                  ["IDE.", "Substituto do K8s.", "Banco de dados."],
                  "Um único agente que recebe OTLP/Jaeger/Zipkin e exporta para múltiplos backends."),
            ],
        },
        # =====================================================================
        # 5.8 Security Chaos Engineering
        # =====================================================================
        {
            "title": "Security Chaos Engineering",
            "summary": "Derrubar partes do sistema para ver se ele resiste.",
            "lesson": {
                "intro": (
                    "Você tem alertas, runbooks, NetworkPolicy, backup. Tudo no papel parece "
                    "ótimo. Mas funciona <em>de verdade</em>? Chaos engineering responde "
                    "empiricamente: introduz falhas controladas para descobrir fraquezas "
                    "antes de incidente real. Nasceu na Netflix em 2010 (Chaos Monkey). "
                    "Security chaos amplia a ideia para validar controles defensivos, testa "
                    "se SOC detecta exfil simulada, se runbook funciona em invasão, se isolamento "
                    "sobrevive a 1 zona inteira fora."
                ),
                "body": (
                    "<h3>1. Princípios (principlesofchaos.org)</h3>"
                    "<ol>"
                    "<li><strong>Defina steady state</strong>: métrica mensurável de saúde do "
                    "sistema (req success rate, p99, error rate). Sem isso, você não sabe se "
                    "experimento causou regressão.</li>"
                    "<li><strong>Levante hipótese</strong>: 'matar 1 pod web não impacta SLI'. "
                    "Hipótese é falsificável.</li>"
                    "<li><strong>Introduza eventos do mundo real</strong>: latência de rede, "
                    "perda de zona, corrupção de cache, expiração de cert.</li>"
                    "<li><strong>Limite blast radius</strong>: comece minúsculo. 1 pod, 1 "
                    "namespace, 1 região. Tenha kill switch.</li>"
                    "<li><strong>Aprenda e ajuste</strong>: sem ação concreta após, é teatro. "
                    "Cada experimento gera melhorias.</li>"
                    "</ol>"

                    "<h3>2. Steady state na prática</h3>"
                    "<p>Bom steady state:</p>"
                    "<ul>"
                    "<li>'p99 latência &lt; 500ms na rota /checkout'.</li>"
                    "<li>'success rate &gt; 99.5%'.</li>"
                    "<li>'kafka consumer lag &lt; 10s'.</li>"
                    "</ul>"
                    "<p>Ruim:</p>"
                    "<ul>"
                    "<li>'CPU baixa' (não diz nada para o usuário).</li>"
                    "<li>'logs sem erro' (logs podem mentir).</li>"
                    "</ul>"

                    "<h3>3. Tipos de experimento</h3>"
                    "<ul>"
                    "<li><strong>Resiliência</strong>: matar pods, latência de rede, falha de "
                    "DNS, perda de zona AZ, falha de DB primary, cache cold.</li>"
                    "<li><strong>Segurança</strong>: simular vazamento de credencial, tentativa "
                    "de exfiltração, comprometimento de pod, container escape attempt.</li>"
                    "<li><strong>Operacional</strong>: derrubar paginação principal (qual "
                    "secundária funciona?), oncall fora do ar (próximo na lista responde?), "
                    "exec sem runbook (improviso aguenta?).</li>"
                    "</ul>"

                    "<h3>4. Ferramentas</h3>"
                    "<ul>"
                    "<li><strong>Chaos Mesh</strong> (CNCF): K8s-native. CRDs para PodChaos, "
                    "NetworkChaos, IOChaos, KernelChaos, TimeChaos. UI bonita.</li>"
                    "<li><strong>LitmusChaos</strong> (CNCF): outro K8s-native. Hub de "
                    "experimentos prontos.</li>"
                    "<li><strong>AWS Fault Injection Simulator (FIS)</strong>: chaos como serviço "
                    "para EC2/ECS/EKS/RDS.</li>"
                    "<li><strong>Azure Chaos Studio</strong> e <strong>GCP Chaos</strong>: equivalentes.</li>"
                    "<li><strong>Gremlin</strong>: comercial, multi-cloud.</li>"
                    "<li><strong>ChaosMonkey/Simian Army</strong> (Netflix): pioneiros.</li>"
                    "<li><strong>ChaoSlingr</strong>: foco específico em security chaos.</li>"
                    "<li><strong>Toxiproxy</strong> (Shopify): proxy TCP que injeta latência/"
                    "perda, útil para dev local.</li>"
                    "</ul>"

                    "<h3>5. Exemplo Chaos Mesh: matar pods aleatórios</h3>"
                    "<pre><code>apiVersion: chaos-mesh.org/v1alpha1\n"
                    "kind: PodChaos\n"
                    "metadata: { name: kill-web-pods, namespace: prod }\n"
                    "spec:\n"
                    "  action: pod-kill\n"
                    "  mode: one             # 1 pod por vez\n"
                    "  duration: \"30s\"\n"
                    "  selector:\n"
                    "    namespaces: [prod]\n"
                    "    labelSelectors:\n"
                    "      app: web\n"
                    "  scheduler:\n"
                    "    cron: \"@every 10m\"  # a cada 10 min, mata 1 pod web</code></pre>"

                    "<h3>6. Exemplo: latência de rede</h3>"
                    "<pre><code>apiVersion: chaos-mesh.org/v1alpha1\n"
                    "kind: NetworkChaos\n"
                    "metadata: { name: db-slow }\n"
                    "spec:\n"
                    "  action: delay\n"
                    "  mode: all\n"
                    "  selector:\n"
                    "    namespaces: [prod]\n"
                    "    labelSelectors: { app: api }\n"
                    "  delay:\n"
                    "    latency: \"100ms\"\n"
                    "    correlation: \"100\"\n"
                    "    jitter: \"10ms\"\n"
                    "  direction: to\n"
                    "  target:\n"
                    "    selector:\n"
                    "      namespaces: [prod]\n"
                    "      labelSelectors: { app: postgres }\n"
                    "    mode: all\n"
                    "  duration: \"10m\"</code></pre>"
                    "<p>Pergunta: 'p99 sobe quanto? circuit breakers tripam? users veem erro? "
                    "alertas disparam corretamente?'</p>"

                    "<h3>7. Game Day</h3>"
                    "<p>Cenário simulado em sala/Zoom. Roteiro:</p>"
                    "<ol>"
                    "<li><strong>Pre-game</strong>: facilitador define hipótese, blast radius, "
                    "métricas. Time não sabe detalhes específicos.</li>"
                    "<li><strong>Game start</strong>: facilitador injeta falha (real em "
                    "staging, ou tabletop na sala).</li>"
                    "<li><strong>Detecção</strong>: time tenta perceber pelos canais reais "
                    "(alertas, dashboards, customer reports). Mede MTTD.</li>"
                    "<li><strong>Resposta</strong>: time aplica runbook, comunica, executa. "
                    "Mede MTTR.</li>"
                    "<li><strong>Recovery</strong>: time confirma steady state restaurado.</li>"
                    "<li><strong>Postmortem</strong>: o que funcionou, o que falhou, "
                    "action items.</li>"
                    "</ol>"
                    "<p>Resultados típicos: alertas mal-configurados, runbooks desatualizados, "
                    "dependências escondidas, escalation paths inexistentes.</p>"

                    "<h3>8. Security chaos: experimentos específicos</h3>"
                    "<ul>"
                    "<li><strong>Credential leak</strong>: 'esquecer' uma AWS key em repo "
                    "público de teste. Quanto tempo até o secret scanner do CI alertar? "
                    "Quanto até GitHub revogar? Até SOC perceber via CloudTrail?</li>"
                    "<li><strong>Exfil simulada</strong>: pod faz curl para domínio "
                    "manipulado (canary domain). DLP/SIEM detecta?</li>"
                    "<li><strong>Privilege escalation simulada</strong>: simulate setuid attempt "
                    "em container. Falco detecta?</li>"
                    "<li><strong>RBAC excess</strong>: introduzir SA com cluster-admin "
                    "temporário. Auditoria detecta?</li>"
                    "<li><strong>Imagem maliciosa</strong>: imagem com cryptominer disfarçado. "
                    "Image scan + admission policy bloqueiam?</li>"
                    "</ul>"

                    "<h3>9. Em produção?</h3>"
                    "<p>Sim, com cuidado:</p>"
                    "<ol>"
                    "<li><strong>Comece em dev/staging</strong> com volume.</li>"
                    "<li>Quando houver confiança, GameDay isolado em prod, com janela "
                    "comunicada.</li>"
                    "<li>Defina <strong>kill switch</strong>: comando para parar tudo "
                    "instantaneamente. Teste antes.</li>"
                    "<li>Comunique stakeholders: 'no dia X às Y, vamos derrubar 1 zona em "
                    "região Z por 15 min'.</li>"
                    "<li>Tenha plano B se experimento se torna incidente real.</li>"
                    "<li>Eventualmente: <strong>continuous chaos</strong> em prod com blast "
                    "radius mínimo. Netflix faz há anos.</li>"
                    "</ol>"

                    "<h3>10. Métricas e ROI</h3>"
                    "<ul>"
                    "<li><strong>MTTD</strong> (mean time to detect): tempo até alerta válido.</li>"
                    "<li><strong>MTTR</strong> (mean time to recover): tempo até steady state.</li>"
                    "<li><strong>Findings por experimento</strong>: bugs em runbook, alertas "
                    "que não tocaram, dependências escondidas.</li>"
                    "<li><strong>Action items completados</strong>.</li>"
                    "<li><strong>Reduções de incidente real após chaos</strong> (mais difícil "
                    "de medir, mas a justificativa final).</li>"
                    "</ul>"

                    "<h3>11. Maturidade</h3>"
                    "<p>Pirâmide:</p>"
                    "<ol>"
                    "<li>Tabletop exercises (fácil, sem risco).</li>"
                    "<li>Chaos manual em dev/staging (pequenas falhas).</li>"
                    "<li>Game days agendados em prod.</li>"
                    "<li>Continuous chaos em prod com blast radius pequeno.</li>"
                    "<li>Chaos como cultura, todo time tem experimentos próprios.</li>"
                    "</ol>"

                    "<h3>12. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Chaos sem hipótese</strong>: vandalismo. 'Vamos ver o que "
                    "acontece' não gera aprendizado direcionado.</li>"
                    "<li><strong>Sem postmortem com action items</strong>: experimento revela "
                    "buracos, mas ninguém os fecha.</li>"
                    "<li><strong>Blast radius gigante na primeira tentativa</strong>: time "
                    "perde confiança e chaos morre.</li>"
                    "<li><strong>Chaos sem coordenação com SOC</strong>: alertas reais "
                    "ignorados como 'mais um teste'.</li>"
                    "<li><strong>Apenas resilience chaos, sem security</strong>: defesa contra "
                    "atacantes não é exercitada.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Use Chaos Mesh para injetar 100ms de latência em chamadas para o DB de "
                    "uma aplicação em staging por 10 minutos. Meça impacto em p99 e veja se "
                    "alertas configurados disparam. Em seguida, faça experimento de pod-kill "
                    "aleatório a cada 5 min por 1 hora e veja se o cluster recupera. Documente "
                    "em postmortem: hipótese, métricas, findings, action items."
                ),
            },
            "materials": [
                m("Principles of Chaos", "https://principlesofchaos.org/", "article", ""),
                m("Chaos Mesh", "https://chaos-mesh.org/docs/", "docs", ""),
                m("LitmusChaos", "https://litmuschaos.io/docs/", "docs", ""),
                m("Gremlin", "https://www.gremlin.com/community/", "article", ""),
                m("ChaosSlingr (security)", "https://github.com/Optum/ChaoSlingr", "tool", ""),
                m("AWS Fault Injection Simulator",
                  "https://docs.aws.amazon.com/fis/latest/userguide/what-is.html", "docs", ""),
                m("Chaos Engineering: Crash course", "https://www.gremlin.com/chaos-engineering", "course", "Curso introdutório."),
            ],
            "questions": [
                q("Chaos engineering:",
                  "Experimentos controlados para descobrir fraquezas.",
                  ["Hackear com aleatoriedade.", "Apagar prod.", "Sem hipótese."],
                  "Não é vandalismo: cada experimento tem hipótese, métrica e blast radius."),
                q("Game day:",
                  "Cenário simulado para testar runbooks e o time.",
                  ["Festa.", "DDoS público.", "Backup automático."],
                  "Pratica resposta sem o estresse de incidente real. Identifica buracos em runbooks."),
                q("Hipótese científica:",
                  "Necessária antes do experimento.",
                  ["Apenas em academia.", "Sem importância.", "Inviabiliza testes."],
                  "Sem hipótese, qualquer resultado é 'descoberta interessante', mas não testável."),
                q("Blast radius:",
                  "Limite de impacto do experimento.",
                  ["Sempre tudo.", "Apenas DNS.", "Apenas dev."],
                  "Comece pequeno (1 pod), expanda gradualmente. Tenha kill switch."),
                q("Exfiltração simulada:",
                  "Verifica detecção/resposta como em ataque real.",
                  ["Substitui audit.", "Sempre bloqueado.", "Sem valor."],
                  "Red team injeta tráfego para domínio suspeito; SOC deveria detectar."),
                q("Métrica chave:",
                  "MTTD (mean time to detect) e MTTR.",
                  ["Apenas custo.", "Tamanho do log.", "Reqs/s."],
                  "Detectar e recuperar rápido = menor impacto. Chaos mede ambos."),
                q("Chaos em prod:",
                  "Sim, com cuidado e plano de rollback.",
                  ["Nunca.", "Sempre destrutivo.", "Sem necessidade."],
                  "Netflix faz há anos. Comece em janelas controladas com kill switch."),
                q("LitmusChaos é:",
                  "Plataforma OSS para chaos em K8s.",
                  ["IDE.", "Substituto do Argo.", "Backup."],
                  "CNCF incubating. CRDs para experimentos versionados em Git."),
                q("Sem aprendizado pós-experimento:",
                  "Chaos vira teatro.",
                  ["É inevitável.", "Adiciona valor.", "Não acontece."],
                  "Ação real (corrigir, melhorar runbook, automatizar) é o propósito."),
                q("Postmortem em chaos:",
                  "Captura findings e ações de resiliência.",
                  ["Apenas se houver downtime.", "Substitui experimento.", "Decisão única."],
                  "Mesmo experimento bem-sucedido gera lições. Documente."),
            ],
        },
        # =====================================================================
        # 5.9 Incident Response
        # =====================================================================
        {
            "title": "Incident Response",
            "summary": "Automação para bloquear ataques automaticamente.",
            "lesson": {
                "intro": (
                    "Quando o incidente acontece, e vai acontecer, o tempo conta em minutos, "
                    "não horas. Equipes que praticam respondem em 10 min; equipes que não "
                    "praticam levam 10 horas. A diferença não é talento; é preparação. "
                    "Runbooks, papéis claros, comunicação coordenada e automação podem "
                    "reduzir MTTR (mean time to recover) drasticamente. Este tópico cobre o "
                    "framework NIST 800-61 e práticas modernas (SOAR, blameless postmortem)."
                ),
                "body": (
                    "<h3>1. NIST SP 800-61, as 4 fases</h3>"
                    "<ol>"
                    "<li><strong>Preparation</strong>: tudo que se faz <em>antes</em> de "
                    "incidente. Runbooks, treinos, ferramentas, contatos atualizados, acessos "
                    "break-glass. É a fase mais subestimada e a mais importante.</li>"
                    "<li><strong>Detection &amp; Analysis</strong>: alertas, SIEM, triagem, "
                    "classificação. Falsos positivos vs incidentes reais. Determinar escopo "
                    "e severidade.</li>"
                    "<li><strong>Containment, Eradication &amp; Recovery</strong>: limitar "
                    "avanço, remover artefatos do invasor, restaurar serviço.</li>"
                    "<li><strong>Post-Incident Activity</strong>: postmortem blameless, "
                    "action items, atualizações de runbook, treinamento.</li>"
                    "</ol>"
                    "<p>O framework é cíclico: lições da fase 4 alimentam fase 1.</p>"

                    "<h3>2. Funções no incidente</h3>"
                    "<p>Em incidentes pequenos, mesma pessoa pode acumular. Em grandes, "
                    "separar é vital, pessoa que decide não pode estar com mãos no teclado:</p>"
                    "<ul>"
                    "<li><strong>Incident Commander (IC)</strong>: decide. Coordena. Aprova "
                    "ações de risco. Mantém timeline mental. <em>Não</em> mexe em sistemas.</li>"
                    "<li><strong>Operações / Tech Lead</strong>: implementa ações no sistema.</li>"
                    "<li><strong>Comunicação</strong>: stakeholders internos, clientes, "
                    "imprensa se necessário. Mantém status page.</li>"
                    "<li><strong>Scribe</strong>: anota timeline em tempo real (Slack thread, "
                    "Google Doc). Vital para postmortem.</li>"
                    "<li><strong>Security Lead</strong> (em incidentes de segurança): "
                    "preserva evidência, coordena forensics.</li>"
                    "</ul>"

                    "<h3>3. Severidade</h3>"
                    "<p>Definir <em>antes</em>:</p>"
                    "<ul>"
                    "<li><strong>SEV1</strong>: indisponibilidade total ou exposição grave de "
                    "dados. Pager 24/7. Comunicação imediata. Ex.: prod down, breach "
                    "confirmado, RCE pública.</li>"
                    "<li><strong>SEV2</strong>: degradação significativa ou risco real. "
                    "Resposta em ≤1h. Ex.: 1 região fora, latência 5x.</li>"
                    "<li><strong>SEV3</strong>: bug isolado, problema parcial. Horário "
                    "comercial.</li>"
                    "<li><strong>SEV4</strong>: cosmético, baixa prioridade.</li>"
                    "</ul>"
                    "<p>Critérios devem ser explícitos para evitar arbítrio às 3am.</p>"

                    "<h3>4. Comunicação durante incidente</h3>"
                    "<ul>"
                    "<li><strong>Canal dedicado</strong>: <code>#inc-2026-04-25-auth-down</code>. "
                    "Não use canais pessoais (perdem auditoria, contexto polui).</li>"
                    "<li><strong>Bridge de voz</strong> (Zoom/Meet): para discussão rápida.</li>"
                    "<li><strong>Status page</strong>: público (statuspage.io, Better Stack) "
                    "para clientes. Atualize periodicamente, silêncio é pior que más notícias.</li>"
                    "<li><strong>Update template</strong>:"
                    "<pre><code>UPDATE 14:30 UTC: continuamos investigando latência elevada\n"
                    "no checkout. Times de pagamento e infra envolvidos. Próximo update: 15:00.</code></pre>"
                    "</li>"
                    "<li><strong>Escalation matrix</strong>: quem chamar quando IC não responde, "
                    "quando exec precisa saber, quando legal entra.</li>"
                    "</ul>"

                    "<h3>5. Containment estratégico</h3>"
                    "<p>Curto prazo: <em>parar o sangramento</em>:</p>"
                    "<ul>"
                    "<li>Isolar pod/host (NetworkPolicy, taint).</li>"
                    "<li>Revogar credencial (kill JWT, rotacionar key).</li>"
                    "<li>Desligar feature toggle.</li>"
                    "<li>Block IP em WAF.</li>"
                    "</ul>"
                    "<p>Longo prazo: <em>preparar erradicação</em>:</p>"
                    "<ul>"
                    "<li>Snapshot/forensics antes de destruir.</li>"
                    "<li>Identificar IOCs (IPs, hashes, domínios).</li>"
                    "<li>Mapear extensão do comprometimento.</li>"
                    "</ul>"

                    "<h3>6. Eradication &amp; Recovery</h3>"
                    "<ul>"
                    "<li>Rebuild de imagens/containers do zero.</li>"
                    "<li>Rotação de <em>todos</em> segredos do escopo (não só os comprometidos "
                    "comprovadamente).</li>"
                    "<li>Patch da vulnerabilidade root.</li>"
                    "<li>Restore de backup (se ransomware/destruição).</li>"
                    "<li>Validação: serviço voltou ao steady state?</li>"
                    "<li>Monitoramento intensificado por dias após.</li>"
                    "</ul>"

                    "<h3>7. Postmortem blameless</h3>"
                    "<p>Foco em <em>sistemas</em>, não pessoas. Pergunta-chave: 'como o sistema "
                    "permitiu que o erro humano causasse impacto?' em vez de 'quem errou?'.</p>"
                    "<p>Estrutura típica:</p>"
                    "<ol>"
                    "<li><strong>Sumário executivo</strong>: 2-3 linhas para nível C.</li>"
                    "<li><strong>Impacto</strong>: tempo de duração, % de usuários afetados, "
                    "$ perdido, dados expostos.</li>"
                    "<li><strong>Timeline detalhada</strong>: cada ação com timestamp.</li>"
                    "<li><strong>Root cause analysis</strong> (5 whys, fishbone): cadeia de "
                    "causas.</li>"
                    "<li><strong>O que funcionou bem</strong>: importantíssimo, celebra acertos, "
                    "preserva práticas.</li>"
                    "<li><strong>O que pode melhorar</strong>: detecção, resposta, prevenção.</li>"
                    "<li><strong>Action items</strong>: cada um com <em>owner, prazo, ticket "
                    "rastreável</em>. Sem isso, postmortem é narrativa.</li>"
                    "</ol>"
                    "<p>Exemplo de '5 Whys':</p>"
                    "<pre><code>Sintoma: API ficou 30 min fora.\n"
                    "Por quê? Pod web entrou em CrashLoopBackOff.\n"
                    "Por quê? Liveness probe começou a falhar quando DB ficou lento.\n"
                    "Por quê? Probe fazia query no DB (acoplamento ruim).\n"
                    "Por quê? Template antigo da empresa, nunca questionado.\n"
                    "Por quê? Nenhuma revisão de templates desde 2 anos.\n"
                    "Action item: revisar todos templates de Deployment para liveness mais leve.</code></pre>"

                    "<h3>8. SOAR (Security Orchestration, Automation and Response)</h3>"
                    "<p>SOAR automatiza playbooks repetitivos. Quando alerta de tipo X dispara:</p>"
                    "<ol>"
                    "<li>Enriquecer alerta (lookup IP em threat intel, GeoIP, WHOIS).</li>"
                    "<li>Verificar se é falso positivo conhecido.</li>"
                    "<li>Aplicar containment (bloquear IP em WAF, isolar pod).</li>"
                    "<li>Abrir ticket.</li>"
                    "<li>Notificar canal.</li>"
                    "<li>Esperar humano para decisão de escalation.</li>"
                    "</ol>"
                    "<p>Ferramentas: Splunk SOAR (Phantom), Tines, n8n, Shuffle, Demisto.</p>"

                    "<h3>9. Threat intelligence e IOCs</h3>"
                    "<ul>"
                    "<li><strong>IOC</strong> (Indicator of Compromise): hash de malware, IP "
                    "C2, domínio, user agent, comportamento.</li>"
                    "<li><strong>STIX/TAXII</strong>: padrões para troca de threat intel.</li>"
                    "<li><strong>MISP</strong>: plataforma open-source para intel.</li>"
                    "<li><strong>ISACs</strong>: setoriais (FS-ISAC para financeiro).</li>"
                    "</ul>"
                    "<p>Compartilhar IOCs com peers acelera defesa coletiva. Receber também.</p>"

                    "<h3>10. MITRE ATT&amp;CK e D3FEND</h3>"
                    "<ul>"
                    "<li><strong>ATT&amp;CK</strong>: táticas/técnicas de adversários.</li>"
                    "<li><strong>D3FEND</strong>: contramedidas defensivas mapeadas para "
                    "ATT&amp;CK.</li>"
                    "</ul>"
                    "<p>Em postmortem, mapeie cada técnica observada para ATT&amp;CK. Em "
                    "preparation, identifique gaps em D3FEND.</p>"

                    "<h3>11. Tabletop exercises</h3>"
                    "<p>Simulação verbal, sem mexer em sistemas reais:</p>"
                    "<ol>"
                    "<li>Facilitador descreve cenário ('às 3am, alerta indica vazamento de "
                    "10GB para IP suspeito').</li>"
                    "<li>Participantes descrevem o que fariam.</li>"
                    "<li>Facilitador injeta complicações ('mas o oncall principal está em "
                    "férias e o secundário não responde').</li>"
                    "<li>Discussão revela buracos em runbook, comunicação, escalation.</li>"
                    "</ol>"
                    "<p>Barato, alta-frequência, alto-impacto. Faça trimestralmente.</p>"

                    "<h3>12. Postmortem culture: mistakes welcome</h3>"
                    "<p>Cultura blameless é o trabalho mais difícil. Sinais de cultura "
                    "saudável:</p>"
                    "<ul>"
                    "<li>Escrever postmortem não é punição.</li>"
                    "<li>Compartilhar postmortems internamente (até com nível C).</li>"
                    "<li>Discutir 'near misses' (incidentes que quase aconteceram).</li>"
                    "<li>Action items são rastreados e completados.</li>"
                    "<li>Sem caça aos culpados; cada pessoa fez o melhor que podia com info "
                    "que tinha.</li>"
                    "</ul>"

                    "<h3>13. Métricas operacionais</h3>"
                    "<ul>"
                    "<li><strong>MTTD</strong>: tempo até detecção. Meta: minutos.</li>"
                    "<li><strong>MTTA</strong>: tempo até reconhecimento (ack do pager). Meta: &lt;5min.</li>"
                    "<li><strong>MTTR</strong>: tempo até recovery. Meta: depende, mas trending down.</li>"
                    "<li><strong>Frequência de incidentes por sev</strong>.</li>"
                    "<li><strong>Action items completados</strong>.</li>"
                    "<li><strong>Repetição de causa-raiz</strong>: mesma falha 3x = problema sistêmico.</li>"
                    "</ul>"

                    "<h3>14. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Sem runbook</strong>: improviso às 3am.</li>"
                    "<li><strong>Runbook não testado</strong>: 50% chance de estar errado.</li>"
                    "<li><strong>Comunicação por DM/WhatsApp pessoal</strong>: sem auditoria.</li>"
                    "<li><strong>IC mexendo no teclado</strong>: ninguém coordena.</li>"
                    "<li><strong>Postmortem buscando culpado</strong>: equipe esconde info na "
                    "próxima.</li>"
                    "<li><strong>Action items sem owner/prazo</strong>: nada acontece.</li>"
                    "<li><strong>Severidade arbitrária</strong>: alguns SEV1, outros 'a gente "
                    "vê amanhã'.</li>"
                    "</ul>"

                    "<h3>15. Roadmap pragmático</h3>"
                    "<ol>"
                    "<li>Definir critérios de severidade.</li>"
                    "<li>Implementar canal de incidente, status page, escalation matrix.</li>"
                    "<li>Escrever runbooks para top 5 cenários conhecidos.</li>"
                    "<li>Tabletop exercise mensal.</li>"
                    "<li>Sempre que incidente real: postmortem dentro de 5 dias úteis.</li>"
                    "<li>SOAR para playbooks repetitivos (ranking por frequência).</li>"
                    "<li>Game days trimestrais com chaos engineering.</li>"
                    "</ol>"
                ),
                "practical": (
                    "Crie runbook 'pod comprometido': aplique NetworkPolicy bloqueando egress, "
                    "adicione label <code>quarantine=true</code>, faça snapshot do pod, notifique "
                    "canal #incident. Automatize via webhook do Falco → workflow do Argo Events. "
                    "Em seguida, faça tabletop exercise com 2 colegas: 'às 2h chega alerta de "
                    "exfil de 5GB para domínio russo', pratique IC/Operations/Comms roles."
                ),
            },
            "materials": [
                m("NIST SP 800-61r2", "https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final", "docs", ""),
                m("Atlassian: Incident Mgmt Handbook", "https://www.atlassian.com/incident-management", "article", ""),
                m("PagerDuty Incident Response", "https://response.pagerduty.com/", "article", ""),
                m("Google SRE: Incident Response", "https://sre.google/workbook/incident-response/", "book", ""),
                m("MITRE D3FEND", "https://d3fend.mitre.org/", "docs", ""),
                m("Postmortem template (Google)",
                  "https://sre.google/sre-book/postmortem-culture/", "article", ""),
                m("MISP Threat Sharing", "https://www.misp-project.org/", "tool", "Plataforma de IOC."),
            ],
            "questions": [
                q("Primeira fase do NIST IR:",
                  "Preparation.",
                  ["Recovery.", "Eradication.", "Postmortem."],
                  "Tudo começa antes do incidente: runbooks, treinos, contatos atualizados, ferramentas prontas."),
                q("MTTD mede:",
                  "Tempo para detectar incidente.",
                  ["Tempo para escrever postmortem.", "Tempo de cripto.", "Latência."],
                  "Se MTTD é horas, atacante já fez o estrago. Aim: minutos."),
                q("Runbook deve ser:",
                  "Acionável, versionado e testado em game days.",
                  ["Apenas teórico.", "Em e-mail.", "Confidencial sem testes."],
                  "Sem teste, runbook tem 50% de chance de estar errado quando importa."),
                q("Containment é:",
                  "Limitar avanço do invasor.",
                  ["Apagar evidência.", "Postar na imprensa.", "Reiniciar prod."],
                  "Curto prazo: cortar acesso. Longo prazo: erradicar persistência."),
                q("Postmortem deve:",
                  "Ser blameless e gerar action items.",
                  ["Esconder o ocorrido.", "Punir alguém.", "Ser secreto."],
                  "Cultura de aprendizado é mais valiosa que culpado. Sem action item, postmortem é narrativa."),
                q("SOAR automatiza:",
                  "Playbooks de resposta repetitivos.",
                  ["Substitui SIEM.", "Substitui antivirus.", "Apenas DNS."],
                  "Tempo manual em incidente pequeno → segundos em pipeline."),
                q("Comunicação durante incidente:",
                  "Canal dedicado, bridge e quem assume comando.",
                  ["Apenas e-mail.", "WhatsApp pessoal.", "Sem comunicação."],
                  "Sem command, time corre em direções diferentes. IC mantém ordem."),
                q("Indicador de comprometimento (IOC):",
                  "Sinal observável (hash, IP, comportamento).",
                  ["Cadência de testes.", "Tipo de TLS.", "DNS apenas."],
                  "Alimenta SIEM/EDR para detecção. Compartilhe via STIX/TAXII com peers."),
                q("Tabletop exercise:",
                  "Simulação discutida sem mexer em sistemas reais.",
                  ["Recreação física.", "Hackathon.", "Apenas com red team."],
                  "Fácil de organizar; revela gaps em runbook e comunicação rapidamente."),
                q("Severidade SEV1:",
                  "Indisponibilidade total ou exposição grave.",
                  ["Aviso menor.", "Bug em dev.", "Erro UI."],
                  "Convoca pager 24/7. Critérios devem estar documentados para evitar arbítrio."),
            ],
        },
        # =====================================================================
        # 5.10 Compliance Contínuo
        # =====================================================================
        {
            "title": "Compliance Contínuo",
            "summary": "Garantir que o sistema segue leis (como a LGPD) o tempo todo.",
            "lesson": {
                "intro": (
                    "Compliance manual em planilha não escala. Auditorias anuais que viram "
                    "pesadelo de 3 meses são desperdício. <strong>Continuous compliance</strong> "
                    "é a aplicação dos mesmos princípios de DevOps a auditoria: regras como "
                    "código, evidências automatizadas, dashboards em tempo real. Auditoria deixa "
                    "de ser evento traumático para virar relatório quase-instantâneo. Cobre "
                    "LGPD, GDPR, SOC 2, ISO 27001, PCI DSS, os frameworks mais comuns na "
                    "indústria."
                ),
                "body": (
                    "<h3>1. Frameworks principais</h3>"
                    "<ul>"
                    "<li><strong>LGPD</strong> (Lei Geral de Proteção de Dados, Brasil 2018): "
                    "proteção de dados pessoais. Princípios, bases legais, direitos do titular, "
                    "obrigações do controlador/operador, RIPD, DPO. Multas até R$50M por "
                    "infração ou 2% do faturamento.</li>"
                    "<li><strong>GDPR</strong> (UE 2018): equivalente europeu, multas até 4% do "
                    "faturamento global ou €20M.</li>"
                    "<li><strong>ISO 27001</strong>: norma para SGSI (Sistema de Gestão de "
                    "Segurança da Informação). Anexo A com 93 controles. Certificação anual "
                    "por auditor acreditado.</li>"
                    "<li><strong>SOC 2</strong> (Service Organization Control): trust services "
                    "criteria (Security, Availability, Processing Integrity, Confidentiality, "
                    "Privacy). Type I = design pontual; Type II = operação ao longo de 6+ "
                    "meses. Padrão de mercado para SaaS B2B nos EUA.</li>"
                    "<li><strong>PCI DSS</strong>: empresas que tratam dados de cartão. 12 "
                    "requisitos amplos. Mesmo usando Stripe há controles de escopo.</li>"
                    "<li><strong>HIPAA</strong>: dados de saúde nos EUA.</li>"
                    "<li><strong>NIST CSF</strong>: framework voluntário, organizando práticas "
                    "em Identify/Protect/Detect/Respond/Recover.</li>"
                    "<li><strong>FedRAMP</strong>: governo dos EUA na cloud.</li>"
                    "</ul>"

                    "<h3>2. Princípios LGPD em detalhe</h3>"
                    "<ul>"
                    "<li><strong>Finalidade</strong>: tratamento para propósito legítimo, "
                    "específico e explícito. 'Para melhorar nossos serviços' é vago demais.</li>"
                    "<li><strong>Adequação</strong>: tratamento compatível com a finalidade.</li>"
                    "<li><strong>Necessidade</strong>: limitação ao mínimo necessário (não "
                    "colete CPF se basta nome).</li>"
                    "<li><strong>Livre acesso</strong>: titular pode consultar dados gratuitamente.</li>"
                    "<li><strong>Qualidade</strong>: dados exatos, claros, atualizados.</li>"
                    "<li><strong>Transparência</strong>: informações sobre o tratamento "
                    "acessíveis.</li>"
                    "<li><strong>Segurança</strong>: medidas técnicas e administrativas.</li>"
                    "<li><strong>Prevenção</strong>: medidas para prevenir danos.</li>"
                    "<li><strong>Não-discriminação</strong>: tratamento não pode ser usado "
                    "para fins discriminatórios.</li>"
                    "<li><strong>Responsabilização</strong>: demonstrar adoção das medidas.</li>"
                    "</ul>"

                    "<h3>3. Bases legais (LGPD art. 7º)</h3>"
                    "<ol>"
                    "<li>Consentimento.</li>"
                    "<li>Cumprimento de obrigação legal/regulatória.</li>"
                    "<li>Tratamento por administração pública.</li>"
                    "<li>Estudos por órgão de pesquisa.</li>"
                    "<li>Execução de contrato.</li>"
                    "<li>Exercício regular de direitos em processo judicial.</li>"
                    "<li>Proteção da vida ou incolumidade física.</li>"
                    "<li>Tutela da saúde por profissional/serviço de saúde.</li>"
                    "<li><strong>Legítimo interesse</strong> (com balanceamento).</li>"
                    "<li>Proteção do crédito.</li>"
                    "</ol>"
                    "<p>Cada tratamento <em>tem que</em> mapear a uma base. Inventário de "
                    "tratamentos é exigência prática.</p>"

                    "<h3>4. Papéis (LGPD)</h3>"
                    "<ul>"
                    "<li><strong>Controlador</strong>: decide o tratamento (a empresa).</li>"
                    "<li><strong>Operador</strong>: processa em nome do controlador (AWS, "
                    "fornecedor de e-mail).</li>"
                    "<li><strong>DPO/Encarregado</strong>: ponto de contato com ANPD e "
                    "titulares. Nome e contato divulgados publicamente.</li>"
                    "<li><strong>ANPD</strong>: Autoridade Nacional de Proteção de Dados.</li>"
                    "<li><strong>Titular</strong>: pessoa natural a quem se referem os dados.</li>"
                    "</ul>"

                    "<h3>5. Direitos do titular (art. 18)</h3>"
                    "<ol>"
                    "<li>Confirmação da existência de tratamento.</li>"
                    "<li>Acesso aos dados.</li>"
                    "<li>Correção de dados.</li>"
                    "<li>Anonimização, bloqueio ou eliminação.</li>"
                    "<li>Portabilidade.</li>"
                    "<li>Eliminação dos dados tratados com consentimento.</li>"
                    "<li>Informação das entidades com as quais o controlador compartilhou.</li>"
                    "<li>Informação sobre não fornecer consentimento.</li>"
                    "<li>Revogação do consentimento.</li>"
                    "</ol>"
                    "<p>Operacionalize via portal de privacidade ('Privacy Center') com "
                    "fluxo automatizado para DSAR (Data Subject Access Request). Prazo: 15 "
                    "dias na LGPD.</p>"

                    "<h3>6. RIPD / DPIA</h3>"
                    "<p>Relatório de Impacto à Proteção de Dados (LGPD) / Data Protection "
                    "Impact Assessment (GDPR). Obrigatório quando tratamento envolve risco "
                    "alto (categoria sensível, decisão automatizada, dados de menores, "
                    "monitoramento sistemático). Conteúdo:</p>"
                    "<ul>"
                    "<li>Descrição do tratamento.</li>"
                    "<li>Finalidade.</li>"
                    "<li>Categorias de dados e titulares.</li>"
                    "<li>Avaliação de necessidade e proporcionalidade.</li>"
                    "<li>Riscos identificados e probabilidade/impacto.</li>"
                    "<li>Medidas de mitigação.</li>"
                    "<li>Aprovação/parecer do DPO.</li>"
                    "</ul>"

                    "<h3>7. Continuous compliance: a ideia</h3>"
                    "<p>Em vez de auditoria pontual:</p>"
                    "<ol>"
                    "<li>Defina cada controle como código (regra que pode ser avaliada).</li>"
                    "<li>Avalie continuamente o estado real do ambiente contra controles.</li>"
                    "<li>Gere evidências (logs, screenshots automáticos, exports).</li>"
                    "<li>Armazene em local imutável (WORM).</li>"
                    "<li>Em auditoria, auditor consulta a plataforma, não pede print de tela.</li>"
                    "</ol>"

                    "<h3>8. Ferramentas de continuous compliance</h3>"
                    "<ul>"
                    "<li><strong>AWS Config / Azure Policy / GCP Org Policies</strong>: "
                    "detectam desvios em recursos cloud.</li>"
                    "<li><strong>Cloud Custodian</strong>: policy + remediation em YAML, "
                    "multi-cloud.</li>"
                    "<li><strong>Drata, Vanta, Sprinto, Tugboat Logic, Secureframe</strong>: "
                    "SaaS de continuous compliance que coletam evidências de várias "
                    "plataformas (cloud, GitHub, IdP, MDM, RH) e mantêm dashboard de "
                    "compliance vs framework (SOC 2, ISO 27001).</li>"
                    "<li><strong>OpenSCAP</strong>: validação contra benchmarks SCAP em "
                    "Linux.</li>"
                    "<li><strong>Compliance Operator (OpenShift)</strong>: kube-bench + "
                    "policies em K8s.</li>"
                    "<li><strong>OneTrust, BigID, OneTrust Vendorpedia</strong>: privacidade "
                    "e third-party.</li>"
                    "</ul>"

                    "<h3>9. AWS Config exemplo</h3>"
                    "<pre><code># habilitar regra: bucket S3 não pode ser público\n"
                    "$ aws configservice put-config-rule \\\n"
                    "  --config-rule '{\n"
                    "    \"ConfigRuleName\": \"s3-bucket-public-read-prohibited\",\n"
                    "    \"Source\": {\n"
                    "      \"Owner\": \"AWS\",\n"
                    "      \"SourceIdentifier\": \"S3_BUCKET_PUBLIC_READ_PROHIBITED\"\n"
                    "    }\n"
                    "  }'\n"
                    "\n"
                    "# Conformance Pack: agrupa regras para frameworks\n"
                    "$ aws configservice put-conformance-pack \\\n"
                    "  --conformance-pack-name lgpd-baseline \\\n"
                    "  --template-s3-uri s3://my-bucket/lgpd-pack.yaml</code></pre>"

                    "<h3>10. Evidência como código</h3>"
                    "<p>Tudo gerado automaticamente:</p>"
                    "<ul>"
                    "<li>Saída de pipeline (lint, SAST, scan, DAST).</li>"
                    "<li>Saída de kube-bench, kubescape.</li>"
                    "<li>Exports do AWS Config / Azure Policy.</li>"
                    "<li>Logs de IAM (CloudTrail, Audit log GCP).</li>"
                    "<li>Logs de acesso (VPC Flow Logs, etc.).</li>"
                    "<li>Reports de SCA, SBOM, image scan.</li>"
                    "<li>Logs de revisões de código (PR aprovado por X).</li>"
                    "<li>Logs de treinamentos de funcionários (LMS).</li>"
                    "<li>Configurações de MDM (laptops criptografados? screen lock?).</li>"
                    "</ul>"
                    "<p>Armazene em bucket S3 com Object Lock (WORM) e retenção. Auditor recebe "
                    "URL pré-assinada com TTL.</p>"

                    "<h3>11. Tagging para escopo de dados</h3>"
                    "<pre><code>tags:\n"
                    "  data_classification: pii  # public, internal, pii, phi, pci\n"
                    "  retention_days: 365\n"
                    "  owner: team-billing\n"
                    "  compliance: lgpd,sox\n"
                    "  env: prod</code></pre>"
                    "<p>Permite policy 'todo recurso com data_classification=pii deve ter "
                    "encryption=enabled, ser private, ter logging ativo'. Cloud Custodian "
                    "audita.</p>"

                    "<h3>12. Práticas no dia-a-dia</h3>"
                    "<ul>"
                    "<li>Inventário de tratamentos atualizado.</li>"
                    "<li>Criptografia em trânsito e em repouso em <em>tudo</em>.</li>"
                    "<li>Direito de acesso/exclusão automatizado (DSAR portal).</li>"
                    "<li>Treinamento anual de colaboradores (LGPD/segurança).</li>"
                    "<li>Política de retenção/expurgo automatizada (lifecycle policies).</li>"
                    "<li>DPA (Data Processing Agreement) com cada operador.</li>"
                    "<li>Monitoramento de acesso a dados sensíveis (DAM, audit).</li>"
                    "<li>Notificação de incidente em ≤72h (LGPD/GDPR).</li>"
                    "</ul>"

                    "<h3>13. SOC 2 em detalhe</h3>"
                    "<p>5 Trust Services Criteria (TSC):</p>"
                    "<ol>"
                    "<li><strong>Security</strong>: obrigatório. Controles para proteger "
                    "sistemas.</li>"
                    "<li><strong>Availability</strong>: SLAs de disponibilidade.</li>"
                    "<li><strong>Processing Integrity</strong>: precisão do processamento.</li>"
                    "<li><strong>Confidentiality</strong>: dados confidenciais.</li>"
                    "<li><strong>Privacy</strong>: dados pessoais (similar a LGPD).</li>"
                    "</ol>"
                    "<p>Type I = design no ponto. Type II = operação ao longo de 6+ meses "
                    "(mais valorizado). Auditor independente CPA emite o relatório.</p>"

                    "<h3>14. ISO 27001: estrutura</h3>"
                    "<ul>"
                    "<li><strong>Cláusulas 4-10</strong>: Sistema de Gestão (PDCA).</li>"
                    "<li><strong>Anexo A</strong>: 93 controles em 4 grupos (Organizacionais, "
                    "Pessoas, Físicos, Tecnológicos) na versão 2022.</li>"
                    "<li><strong>SoA</strong> (Statement of Applicability): documento dizendo "
                    "quais controles aplicam, quais não, e por quê.</li>"
                    "<li>Auditoria interna anual + externa para certificação (3 anos com "
                    "vigilâncias intermediárias).</li>"
                    "</ul>"

                    "<h3>15. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Compliance theater</strong>: políticas que ninguém lê, "
                    "controles que ninguém aplica, evidências fabricadas para auditor.</li>"
                    "<li><strong>Auditoria 1x/ano em pânico</strong>: continuous deveria mostrar "
                    "estado atual o tempo todo.</li>"
                    "<li><strong>Privacy by accident</strong>: 'a gente vai pensar em LGPD "
                    "depois'. Privacy by design é a única forma sustentável.</li>"
                    "<li><strong>DPO sem autoridade</strong>: cargo sem poder não funciona.</li>"
                    "<li><strong>Operador sem DPA</strong>: você é responsável pelos dados que "
                    "ele processa por você.</li>"
                    "<li><strong>Tags inconsistentes</strong>: impossível avaliar escopo de dados.</li>"
                    "</ul>"

                    "<h3>16. Roadmap pragmático</h3>"
                    "<ol>"
                    "<li>Identifique o framework prioritário (cliente B2B exige SOC 2? "
                    "Atende público BR? LGPD é mínimo).</li>"
                    "<li>Gap analysis: onde está vs onde precisa estar.</li>"
                    "<li>Implemente controles fundamentais (encryption, MFA, RBAC, audit log, "
                    "backup).</li>"
                    "<li>Tag e classifique dados.</li>"
                    "<li>Continuous compliance tool (Drata/Vanta para SaaS, AWS Config para "
                    "infra).</li>"
                    "<li>DPA com fornecedores.</li>"
                    "<li>Portal de privacidade.</li>"
                    "<li>Auditoria interna.</li>"
                    "<li>Auditoria externa (Type I → Type II).</li>"
                    "</ol>"
                ),
                "practical": (
                    "Configure AWS Config Rules: <code>s3-bucket-public-read-prohibited</code>, "
                    "<code>encrypted-volumes</code>, <code>iam-password-policy</code>, "
                    "<code>vpc-flow-logs-enabled</code>. Crie um Conformance Pack que agrupe "
                    "10+ regras alinhadas com LGPD. Configure entrega de relatório semanal em "
                    "bucket S3 com Object Lock. Teste violando uma regra (criando bucket público) "
                    "e veja AWS Config marcar como NON_COMPLIANT em minutos."
                ),
            },
            "materials": [
                m("LGPD (texto da lei)", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", "docs", ""),
                m("ISO 27001 overview", "https://www.iso.org/isoiec-27001-information-security.html", "docs", ""),
                m("AWS Config", "https://docs.aws.amazon.com/config/latest/developerguide/", "docs", ""),
                m("OpenSCAP", "https://www.open-scap.org/", "tool", ""),
                m("Cloud Custodian", "https://cloudcustodian.io/", "tool", ""),
                m("ANPD (autoridade BR)", "https://www.gov.br/anpd/pt-br", "docs", ""),
                m("SOC 2 overview (AICPA)", "https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2", "docs", ""),
                m("Drata vs Vanta vs Secureframe (G2)", "https://www.g2.com/categories/security-compliance", "article", "Comparação de continuous compliance SaaS."),
            ],
            "questions": [
                q("LGPD aplica-se a:",
                  "Tratamento de dados pessoais no Brasil.",
                  ["Apenas dados públicos.", "Apenas empresas do BR exportando.", "Apenas dados de menores."],
                  "Aplica também a empresas estrangeiras que tratam dados de pessoas no Brasil."),
                q("Princípio de minimização:",
                  "Coletar apenas os dados necessários para a finalidade.",
                  ["Coletar tudo possível.", "Manter para sempre.", "Compartilhar com qualquer um."],
                  "Pergunta-chave: 'preciso desse dado para a finalidade declarada?'."),
                q("DPIA / RIPD:",
                  "Avaliação de impacto à proteção de dados.",
                  ["Backup.", "DNS.", "Tipo de TLS."],
                  "Obrigatório quando tratamento envolve risco alto. Avalia probabilidade e impacto."),
                q("ISO 27001 é:",
                  "Norma para sistema de gestão de segurança da informação.",
                  ["Tipo de cripto.", "DNS server.", "Cloud provider."],
                  "Foco em SGSI. Anexo A lista 93 controles. Certificação anual."),
                q("SOC 2 Type II:",
                  "Atesta operação dos controles em um período (ex.: 6 meses).",
                  ["Apenas no design.", "Apenas no marketing.", "Apenas em PCI."],
                  "Type I é design pontual; Type II é mais valorizado por mostrar consistência."),
                q("Continuous compliance:",
                  "Detecção automática contínua de desvios.",
                  ["Auditoria anual única.", "Checklist em planilha.", "Ignorar até o auditor."],
                  "AWS Config, Drata, Vanta, alertam quando configuração sai do padrão."),
                q("Evidências como código:",
                  "Geração automatizada e armazenamento auditável.",
                  ["PDF impresso.", "E-mail.", "Print de tela."],
                  "Pipeline gera; bucket WORM guarda. Auditor consulta e verifica."),
                q("DPO é:",
                  "Encarregado de proteção de dados.",
                  ["DevOps Pro Officer.", "Apenas em PCI.", "Cargo de TI."],
                  "Função obrigatória na LGPD. Pode ser interno ou externo."),
                q("PCI DSS aplica-se a:",
                  "Empresas que lidam com dados de cartão de pagamento.",
                  ["Apenas bancos.", "Qualquer e-commerce sem cartões.", "Apenas SaaS."],
                  "Mesmo que você use Stripe, há controles de escopo. PCI tem 12 requisitos amplos."),
                q("Cloud Custodian:",
                  "Engine de policy para detectar e remediar em cloud.",
                  ["IDE.", "Substituto do K8s.", "Backup."],
                  "Policy YAML: filtra recursos + ação (notify/tag/stop/delete). Open source."),
            ],
        },
    ],
}
