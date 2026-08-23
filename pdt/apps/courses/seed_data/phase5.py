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
                """<h3>1. O modelo de ameaça: contra o quê hardening realmente defende</h3>
<p>Aplicar um checklist de hardening sem entender o que ele previne
produz uma falsa sensação de segurança — a lista certa só faz sentido
quando você sabe qual dos cinco cenários abaixo ela fecha. O
<strong>atacante externo</strong> tipicamente começa explorando uma
vulnerabilidade na aplicação web, usa isso para comprometer o container,
e a partir daí tenta escalar para o node e depois para o cluster inteiro
— cada camada de hardening desta aula existe para travar um desses
saltos. O <strong>insider</strong> não precisa de exploit nenhum: é um
desenvolvedor com <code>kubectl</code> tentando acessar um namespace que
não deveria, ou um token de CI com escopo mais amplo do que a tarefa
exige. <strong>Container breakout</strong> explora uma falha no runtime
ou no kernel para escapar do isolamento do container e agir diretamente
no host — o cenário que securityContext e seccomp (seção 4) mais
diretamente mitigam. <strong>Supply chain</strong> é uma imagem
maliciosa puxada de um registry público, comprometendo o cluster antes
mesmo do primeiro deploy acontecer. E <strong>misconfiguração</strong> —
um Secret exposto, um RBAC permissivo demais, encryption nunca
habilitada — é, na prática, a maior fonte real de incidentes, muito mais
comum do que qualquer exploit sofisticado. Nenhum controle isolado
resolve todos os cinco: hardening funciona como defesa em camadas, onde
cada camada cobre o que a anterior deixou passar.</p>

<h3>2. RBAC granular: quatro objetos, e o verbo que ignora todos os outros</h3>
<p>RBAC controla QUEM pode fazer O QUÊ na API do Kubernetes, através de
quatro tipos de objeto: <code>Role</code> define permissões dentro de UM
namespace; <code>ClusterRole</code> define permissões que abrangem o
cluster inteiro ou recursos que não pertencem a namespace nenhum (Node,
PersistentVolume); <code>RoleBinding</code> conecta um Role a um
usuário, grupo ou ServiceAccount específico; <code>ClusterRoleBinding</code>
faz o mesmo para um ClusterRole:</p>
<pre><code>apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: app
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: alice-pod-reader
  namespace: app
subjects:
- kind: User
  name: alice@example.com
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io</code></pre>
<p>A prática recomendada é reservar <code>cluster-admin</code> só para
acesso de emergência ("break-glass") protegido por MFA, e não como
permissão de rotina — para aplicações, conceder MENOS do que parece
necessário de início e ampliar só quando um erro real de permissão
aparecer é mais seguro que o caminho inverso. <code>kubectl auth can-i
--list --as=system:serviceaccount:ns:sa</code> audita exatamente o que
uma ServiceAccount pode fazer, sem precisar ler manualmente cada Role e
Binding. Três verbos merecem atenção redobrada:
<code>create</code>/<code>delete</code> por serem destrutivos, e
especialmente <code>impersonate</code> — que permite a quem o possui agir
COMO qualquer outro usuário ou ServiceAccount, efetivamente contornando
todo o resto do RBAC configurado. E controlar só os verbos não basta:
quem tem permissão de CRIAR Roles com poderes amplos pode elevar o
próprio privilégio criando um Role novo mais permissivo — por isso quem
administra RBAC precisa ser um conjunto de pessoas distinto de quem
apenas usa o cluster no dia a dia.</p>

<h3>3. Pod Security Standards: o substituto do PSP, em três níveis</h3>
<p>Depois da remoção do PodSecurityPolicy (PSP), o Kubernetes passou a
usar Pod Security Standards (PSS), aplicado por LABEL de namespace, com
três níveis de rigor progressivo. <strong>privileged</strong> não impõe
nenhuma restrição — reservado para a infraestrutura do próprio cluster,
não para cargas de trabalho de aplicação. <strong>baseline</strong>
bloqueia o mais óbvio e perigoso (containers privilegiados, hostPID,
hostNetwork, hostPath) mas ainda permite alguma flexibilidade — adequado
para ambiente de desenvolvimento. <strong>restricted</strong> é o
estado da arte: exige <code>runAsNonRoot</code>, descartar todas as
capabilities do Linux por padrão, um perfil seccomp definido, filesystem
raiz somente-leitura — o nível esperado em produção:</p>
<pre><code>kubectl label ns prod \\
  pod-security.kubernetes.io/enforce=restricted \\
  pod-security.kubernetes.io/enforce-version=latest \\
  pod-security.kubernetes.io/warn=restricted \\
  pod-security.kubernetes.io/audit=restricted</code></pre>
<p>Os três modos servem propósitos distintos: <code>enforce</code>
efetivamente BLOQUEIA um pod que viole a política; <code>warn</code>
avisa no momento do <code>kubectl apply</code> sem impedir (útil durante
uma migração gradual para uma política mais estrita); <code>audit</code>
apenas registra a violação no audit-log, sem interromper nada — a
combinação dos três permite rodar em modo "observe antes de bloquear"
antes de ativar enforcement de fato. Para regras mais granulares do que
PSS cobre nativamente, ferramentas como Kyverno e OPA Gatekeeper (vistas
no tópico de Admission Controllers) preenchem a lacuna.</p>

<h3>4. `securityContext`: por que cada flag existe para fechar um vetor específico</h3>
<pre><code>spec:
  containers:
  - name: app
    securityContext:
      runAsNonRoot: true
      runAsUser: 65532
      runAsGroup: 65532
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
        # add: ["NET_BIND_SERVICE"]  # se realmente precisar
  securityContext:
    seccompProfile:
      type: RuntimeDefault
    fsGroup: 65532</code></pre>
<p><code>runAsNonRoot</code> importa porque UID 0 dentro do container
ainda é UID 0 no host (a menos que user namespaces, ainda em fase alpha
no Kubernetes 1.30, estejam habilitados) — um breakout de container que
roda como root herda root no host inteiro.
<code>readOnlyRootFilesystem</code> força a aplicação a usar volumes
específicos para qualquer escrita, o que significa que um atacante que
comprometa o processo não consegue simplesmente escrever um binário
malicioso em <code>/usr/bin</code> — não há onde escrever.
<code>allowPrivilegeEscalation: false</code> bloqueia especificamente a
técnica de escalar privilégio através de um binário com bit setuid.
Descartar TODAS as capabilities do Linux por padrão reconhece que a
maioria das aplicações web não precisa nem de <code>NET_RAW</code> —
adicionar de volta só a capability estritamente necessária (como
<code>NET_BIND_SERVICE</code> para escutar numa porta privilegiada)
mantém a superfície mínima. E <code>seccompProfile: RuntimeDefault</code>
filtra cerca de 70 syscalls consideradas perigosas (como
<code>mount</code> e <code>ptrace</code>), reduzindo o que um processo
comprometido dentro do container consegue pedir ao kernel, mesmo que já
tenha conseguido executar código arbitrário.</p>

<h3>5. NetworkPolicy default-deny: o mínimo para não deixar o cluster inteiro aberto</h3>
<p>Sem NetworkPolicy nenhuma configurada, comprometer UM pod dá acesso de
rede a QUALQUER outro pod do cluster — não há segmentação nenhuma por
padrão. O mínimo viável é negar tudo e liberar explicitamente o que é
necessário:</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# permitir DNS para todo pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: prod }
spec:
  podSelector: {}
  egress:
  - to:
    - namespaceSelector:
        matchLabels: { kubernetes.io/metadata.name: kube-system }
      podSelector:
        matchLabels: { k8s-app: kube-dns }
    ports:
    - protocol: UDP
      port: 53</code></pre>
<p>O detalhe fácil de esquecer: um default-deny sem a exceção de DNS
quebra a resolução de nomes para TODO pod do namespace — a aplicação
para de funcionar de forma que parece um bug de rede aleatório, quando
na verdade é a policy funcionando exatamente como configurada, apenas
sem a exceção necessária. O tópico dedicado de Network Policies detalha
os padrões mais avançados de segmentação; o ponto essencial aqui é
simples: ative default-deny, sempre.</p>

<h3>6. Encryption at rest: por que "base64" não é criptografia</h3>
<p>O etcd guarda todo o estado do cluster, incluindo Secrets e
ConfigMaps — e sem encryption at rest configurada, um dump do etcd
expõe TODOS os segredos do cluster em texto essencialmente legível
(Secrets são codificados em base64 por padrão, uma codificação
REVERSÍVEL sem chave nenhuma, não uma proteção criptográfica de
verdade). Configurar isso no kube-apiserver fecha essa lacuna:</p>
<pre><code># encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - kms:
      name: aws-kms
      endpoint: unix:///var/run/kmsplugin/socket
      cachesize: 1000
  - identity: {}  # fallback (sem cripto)</code></pre>
<p>Em clusters gerenciados (EKS, GKE, AKS), habilitar essa proteção
costuma ser uma única opção de "KMS encryption" na criação do cluster.
Em cluster self-hosted, exige configurar um plugin KMS explicitamente ou
usar o provedor <code>aescbc</code> com uma chave que você mesmo
gerencia — sem essa configuração manual, o comportamento padrão
permanece o menos seguro.</p>

<h3>7. Audit log: a única fonte que reconstrói "quem fez o quê, quando"</h3>
<p>O audit log registra cada chamada feita à API do Kubernetes — sem
ele, investigar um incidente de segurança no cluster significa não ter
nenhum registro confiável de que ações foram tomadas antes, durante e
depois:</p>
<pre><code># audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# secrets/configmaps: log corpo da request/response
- level: RequestResponse
  resources:
  - group: ""
    resources: [secrets, configmaps]
# tudo mais: só metadata
- level: Metadata
  omitStages: [RequestReceived]</code></pre>
<p>A política acima ilustra um trade-off deliberado: registrar o CORPO
completo (<code>RequestResponse</code>) só para recursos sensíveis como
Secrets — o suficiente para saber exatamente o que mudou — enquanto o
resto do tráfego gera apenas metadados (quem, quando, qual verbo), sem o
custo de armazenar e processar o volume completo de toda chamada à API.
Enviar esse log para um SIEM externo (Splunk, Datadog, ELK) é essencial:
em nuvem gerenciada, normalmente já flui automaticamente para
CloudWatch ou Cloud Logging, mas self-hosted exige configurar esse
encaminhamento manualmente.</p>

<h3>8. Tokens de ServiceAccount: o vetor que mais gente esquece de fechar</h3>
<p>Por padrão, TODO pod monta automaticamente o token da ServiceAccount
<code>default</code> em
<code>/var/run/secrets/kubernetes.io/serviceaccount/</code> — mesmo pods
que nunca precisam falar com a API do Kubernetes. Um atacante que
comprometa esse pod encontra esse token pronto para uso, e a partir dele
pode fazer chamadas à API com qualquer permissão que a ServiceAccount
<code>default</code> tiver. A mitigação em três camadas: para pods que
NÃO precisam falar com a API, desligar o auto-mount explicitamente
(<code>automountServiceAccountToken: false</code>); para pods que
precisam, usar uma ServiceAccount DEDICADA com RBAC mínimo, nunca a
<code>default</code> compartilhada; e a partir do Kubernetes 1.21,
"bound tokens" com TTL curto e vinculados a uma audience específica já
vêm habilitados por padrão em ServiceAccounts novas, reduzindo a janela
de uso de um token vazado:</p>
<pre><code>apiVersion: v1
kind: ServiceAccount
metadata: { name: web, namespace: prod }
automountServiceAccountToken: false  # default off
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: web, namespace: prod }
spec:
  template:
    spec:
      serviceAccountName: web
      automountServiceAccountToken: false  # explícito
      # ...</code></pre>

<h3>9. Hardening de imagem: reduzir o que existe para explorar</h3>
<p>Fixar imagens por digest (<code>@sha256:...</code>) em vez de tag
mutável garante que o mesmo deploy sempre puxe exatamente o mesmo
conteúdo — uma tag como <code>latest</code> pode apontar para uma
imagem diferente amanhã, sem nenhum controle sobre o que mudou. Usar
imagens base distroless, chainguard ou wolfi elimina shell e pacotes
extras da imagem final — um atacante que ganhe execução de código dentro
de um container sem shell não consegue nem explorar ferramentas básicas
do sistema que simplesmente não existem ali. Scan contínuo no próprio
registry (Trivy, Grype, ECR/GAR Scanning) detecta vulnerabilidade nova
publicada DEPOIS que a imagem já foi construída, não só no momento do
build. Verificar assinatura (Cosign, aplicado via admission webhook)
garante que só imagens de fontes autorizadas rodem no cluster. E anexar
SBOM documenta exatamente o que compõe cada imagem, essencial quando uma
vulnerabilidade nova é anunciada e a pergunta é "quais dos nossos
sistemas usam esse componente?".</p>

<h3>10. Multi-tenancy: por que namespace sozinho não isola nada de verdade</h3>
<p>Namespace é uma fronteira de ORGANIZAÇÃO, não uma fronteira de
SEGURANÇA forte — dois tenants compartilhando um cluster só em
namespaces separados, sem mais nada, ainda compartilham o mesmo kernel,
o mesmo plano de controle, e potencialmente os mesmos nodes. Isolamento
real exige camadas adicionais: RBAC por namespace controla quem
administra o quê; NetworkPolicy default-deny por namespace impede
tráfego cruzado entre tenants; ResourceQuota limita CPU, RAM e número de
objetos por namespace — sem isso, um tenant mal comportado (ou
comprometido) pode consumir recursos suficientes para afetar todos os
outros; LimitRange define valores padrão de request/limit quando um pod
não declara os próprios; PSS restricted fecha a superfície de container;
isolamento de node via taints, tolerations e nodeSelector coloca cada
tenant em nodes físicos dedicados, a camada mais forte disponível dentro
do mesmo cluster; e Hierarchical Namespaces (HNC) organiza isso em
escala para uma organização grande com muitos times. Para tenants
GENUINAMENTE hostis entre si — o caso de um PaaS multi-cliente onde um
cliente pode ser adversário do outro — a resposta correta é cluster
dedicado por tenant, não namespace: nenhuma combinação de controles
dentro de um único cluster oferece a mesma garantia de isolamento que
clusters fisicamente separados.</p>

<h3>11. Auditoria automatizada: medir o drift antes que ele vire incidente</h3>
<p><strong>kube-bench</strong> avalia o cluster diretamente contra o CIS
Kubernetes Benchmark — rodar em CronJob noturno e abrir ticket
automaticamente para qualquer achado de severidade alta transforma
conformidade de um evento anual estressante numa checagem contínua e
barata. <strong>kubescape</strong> amplia a cobertura combinando NSA/CISA,
MITRE ATT&CK e CIS numa interface mais amigável.
<strong>Trivy K8s</strong> soma scan de manifestos, RBAC e workloads
rodando de fato no cluster. <strong>kubeaudit</strong> e
<strong>polaris</strong> fazem linting estático de manifesto antes mesmo
do deploy acontecer. E Falco/Tetragon (detalhados no tópico de Runtime
Security) cobrem a camada que nenhuma dessas ferramentas estáticas
alcança: comportamento observado em tempo de execução, não configuração
declarada.</p>
<pre><code># Exemplo: rode kube-bench em CronJob
$ kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
$ kubectl logs job/kube-bench</code></pre>

<h3>12. O API server: proteger o único ponto que controla tudo o resto</h3>
<p>O API server é o "castelo" do cluster inteiro — comprometê-lo dá
controle sobre todo o resto. Manter o acesso via endpoint privado, nunca
exposto diretamente à internet pública, elimina a superfície de ataque
mais óbvia. Usar OIDC para autenticação humana (integrado a Google
Workspace, Okta, Azure AD) centraliza identidade num provedor já auditado,
em vez de gerenciar credenciais Kubernetes isoladas. MFA deve ser
obrigatório no PROVEDOR de identidade, não apenas assumido — proteger
só o arquivo kubeconfig local não impede uso de uma credencial roubada
se o provedor de identidade em si não exigir segundo fator. Vincular o
kubeconfig ao laptop de cada pessoa, com TTL curto e renovação via OIDC,
limita a janela de uso de uma credencial vazada. E para acesso SSH aos
nodes propriamente ditos, prefira mecanismos gerenciados (SSM na AWS, IAP
no GCP) a chaves SSH estáticas; em ambiente self-hosted, um bastion host
com chave ed25519 e segundo fator na própria bastion é o mínimo
aceitável.</p>

<h3>13. Backup e disaster recovery: o snapshot que ninguém restaurou ainda não é backup</h3>
<p>Um snapshot diário do etcd (<code>etcdctl snapshot save
snap.db</code>) em local seguro é a base de qualquer recuperação de
desastre — sem ele, perder o etcd significa perder todo o estado do
cluster. Velero complementa isso fazendo backup de objetos do Kubernetes
e volumes persistentes, com capacidade de restaurar até mesmo em um
cluster DIFERENTE do original. A parte mais frequentemente esquecida:
testar o restore de verdade, periodicamente — um backup nunca restaurado
é uma suposição otimista, não uma garantia, exatamente pelo mesmo
motivo que um runbook nunca testado (visto na aula de Incident Response)
tem boa chance de estar errado exatamente quando for preciso.</p>

<h3>14. Cinco anti-padrões que aparecem com frequência incômoda</h3>
<ul>
<li><strong>Tudo cluster-admin para o CI</strong>: comprometer o
pipeline de CI, um alvo cada vez mais visado, equivale a comprometer o
cluster inteiro.</li>
<li><strong>ServiceAccount default com RoleBinding amplo</strong>:
qualquer pod aleatório herda privilégio de administrador sem nenhuma
configuração específica precisar existir.</li>
<li><strong>Sem audit-log configurado</strong>: quando o incidente
acontece, não há nenhum registro para reconstruir o que de fato ocorreu.</li>
<li><strong>"Vamos fazer hardening depois"</strong>: uma dívida técnica
de segurança que só cresce conforme o cluster ganha mais cargas de
trabalho, mais times, mais superfície.</li>
<li><strong>kube-bench rodado uma vez, manualmente</strong>: qualquer
melhoria medida assim regride com o tempo (drift de configuração) sem
que ninguém perceba — só automação contínua sustenta o ganho.</li>
</ul>

<h3>15. Roadmap pragmático, em ordem de impacto por esforço</h3>
<ol>
<li>Revisar quem tem <code>cluster-admin</code> hoje e reduzir
agressivamente — normalmente é a ação de maior impacto por menor
esforço.</li>
<li>Aplicar PSS restricted nos namespaces de produção.</li>
<li>Ativar NetworkPolicy default-deny.</li>
<li>Habilitar encryption at rest no etcd.</li>
<li>Configurar securityContext completo em todos os Deployments.</li>
<li>Rodar kube-bench em CI noturno, com ticket automático para achados
de severidade alta.</li>
<li>Encaminhar audit log para um SIEM.</li>
<li>Adicionar scan de imagem e verificação de assinatura ao pipeline.</li>
<li>Implantar segurança em runtime (Falco), a camada que fecha o que
todo o resto, sendo estático, não alcança.</li>
</ol>"""
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
                """<h3>1. O fluxo dentro do API server: onde admission entra na cadeia</h3>
<p>Um <code>kubectl apply</code> não grava direto no etcd — passa por uma
cadeia de checagens em ordem específica, e entender essa ordem explica por
que admission controllers existem como categoria separada de RBAC.
Primeiro vem <strong>autenticação</strong>: quem está fazendo essa
chamada (certificado, OIDC, token)? Depois <strong>autorização</strong>:
essa identidade TEM PERMISSÃO para fazer essa ação, segundo o RBAC? Só
DEPOIS de passar por autenticação e autorização entra a
<strong>mutating admission</strong>, que pode ALTERAR o request antes de
salvar — injetar um sidecar do Istio, preencher um default que faltou.
Em seguida vem a <strong>validação de schema</strong>, checando se o YAML
está estruturalmente correto conforme a definição da CRD. Depois a
<strong>validating admission</strong> decide se o request, já
possivelmente alterado, PASSA nas regras de negócio — sem mais alterar
nada, só aprovar ou rejeitar. Só então o objeto é persistido no etcd. A
implicação prática: RBAC responde "você pode fazer isso?"; admission
responde "isso que você está fazendo é uma boa ideia?" — são duas
perguntas diferentes, e um usuário com permissão RBAC total ainda pode
ser barrado por uma política de admission que julga o CONTEÚDO do
request, não quem o enviou. Se qualquer admission rejeitar, o etcd nunca
é tocado e o usuário recebe erro imediatamente.</p>

<h3>2. Três formas de implementar admission</h3>
<p>Controllers <strong>built-in</strong> vêm compilados diretamente no
apiserver — <code>NamespaceLifecycle</code>, <code>LimitRanger</code>,
<code>ResourceQuota</code>, <code>ServiceAccount</code> e o próprio
<code>PodSecurity</code> (PSS, visto na aula de Hardening) são exemplos.
<strong>Webhooks externos</strong> permitem que VOCÊ defina a lógica: o
apiserver faz uma chamada HTTPS para um serviço seu, esperando resposta
de aprovação ou rejeição — é o mecanismo por trás de Kyverno e
Gatekeeper (seção 3). <strong>Validating Admission Policy</strong>
(GA a partir do Kubernetes 1.30) representa uma terceira via: policies
escritas em CEL (Common Expression Language), declaradas como um CRD
nativo do próprio Kubernetes, sem precisar rodar nenhum webhook externo
— mais leve operacionalmente, porque elimina a dependência de um serviço
adicional respondendo em tempo real a cada chamada de API.</p>

<h3>3. As engines mais usadas, e o trade-off entre facilidade e poder</h3>
<p><strong>Kyverno</strong> (CNCF Incubating) escreve políticas em YAML
puro, usando a mesma sintaxe que qualquer manifesto Kubernetes — a curva
de aprendizado é a menor entre as opções, e a engine suporta validar,
mutar, GERAR novos recursos automaticamente e até limpar recursos
antigos. <strong>OPA Gatekeeper</strong> (CNCF Graduated, mais maduro)
usa Rego, a linguagem de política do Open Policy Agent — mais poderosa
para lógica complexa, mas com curva de aprendizado real, já que Rego é
uma linguagem declarativa própria que a maioria dos times nunca usou
antes. O modelo do Gatekeeper separa <code>ConstraintTemplate</code>
(define a REGRA em Rego) de <code>Constraint</code> (INSTANCIA essa
regra com parâmetros específicos) — a mesma regra pode gerar várias
constraints diferentes com parâmetros distintos. <strong>jsPolicy</strong>
escreve políticas em TypeScript, para times que preferem uma linguagem de
programação convencional a uma linguagem declarativa dedicada. E
<strong>Validating Admission Policy</strong> (seção 2), sendo nativa do
Kubernetes, tende a ser o caminho de menor atrito para regras mais
simples no futuro, evitando a dependência operacional de uma engine
externa inteira.</p>

<h3>4. Exemplo Kyverno: bloquear a tag `:latest` de forma declarativa</h3>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: disallow-latest-tag }
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: require-image-tag
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "Imagens devem ter tag explícita (não :latest)."
      pattern:
        spec:
          containers:
          - image: "!*:latest"</code></pre>
<p>O padrão <code>"!*:latest"</code> é declarativo o suficiente para
entender à primeira leitura mesmo sem conhecer Kyverno — uma vantagem
real sobre a mesma regra escrita em Rego, que exigiria entender a
sintaxe da linguagem antes de julgar se a lógica está certa.
<code>background: true</code> faz o Kyverno também escanear recursos JÁ
EXISTENTES no cluster contra essa regra, não só os novos que chegarem
daqui em diante — essencial para descobrir violações pré-existentes
antes de promover a policy para bloqueio ativo (seção 7).</p>

<h3>5. Exemplo Gatekeeper: a mesma ideia, com Rego e CRDs</h3>
<pre><code># ConstraintTemplate (Rego)
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata: { name: requiredlabels }
spec:
  crd:
    spec:
      names: { kind: RequiredLabels }
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels: { type: array, items: { type: string } }
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package requiredlabels
      violation[{"msg": msg}] {
        required := input.parameters.labels
        provided := input.review.object.metadata.labels
        missing := required[_]
        not provided[missing]
        msg := sprintf("Label obrigatória '%s' ausente", [missing])
      }
---
# Constraint (instância)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: RequiredLabels
metadata: { name: ns-must-have-owner }
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: [Namespace]
  parameters:
    labels: [owner, team, costcenter]</code></pre>
<p>A separação entre template e constraint é o que dá reuso real: o
MESMO <code>ConstraintTemplate</code> de "labels obrigatórias" pode gerar
uma constraint exigindo <code>[owner, team, costcenter]</code> em
Namespaces e outra exigindo um conjunto diferente de labels em
Deployments — a lógica Rego é escrita uma única vez, os parâmetros
variam por instância.</p>

<h3>6. O catálogo de casos de uso que aparece em praticamente todo cluster de produção</h3>
<p>Bloquear imagens com tag <code>latest</code> ou de registries não
autorizados (visto nas seções 4-5) é só o exemplo mais comum. Exigir
<code>resources.requests/limits</code> em todo pod evita que um único
workload sem limite consuma recursos de forma descontrolada e afete
vizinhos no mesmo node. Exigir labels obrigatórias (owner, team,
costcenter, env) é o que torna possível depois calcular custo por time
ou saber a quem perguntar quando algo quebra. Bloquear
<code>hostPath</code>, <code>privileged</code> e <code>runAsRoot</code>
reforça na admissão o que o securityContext já deveria garantir
(redundância deliberada — a política de admission pega o que uma
configuração manual esquecida deixaria passar). Verificar assinatura
Cosign via sigstore policy controller (seção 10) garante proveniência de
imagem. Auto-injetar sidecars via mutating webhook é como Istio, Linkerd
e o Vault Agent adicionam seus proxies sem exigir que cada time edite
manualmente cada manifesto. Forçar uma <code>storageClass</code>
específica em todo PVC evita que alguém acidentalmente use
armazenamento não replicado para dado crítico. Exigir annotation de
subnet interna num Service <code>LoadBalancer</code> evita exposição
acidental à internet pública. E limitar Ingress a padrões de host
específicos impede um <code>*.example.com</code> genérico demais que
acabaria capturando tráfego não previsto.</p>

<h3>7. Audit, warn, enforce: a progressão que evita rejeição em massa</h3>
<p>Lançar uma política nova direto em modo bloqueante é a forma mais
confiável de fazer um time inteiro rejeitar a iniciativa na primeira vez
que um deploy legítimo é barrado sem aviso prévio. A progressão correta
tem três estágios: <strong>audit</strong> apenas registra o que SERIA
bloqueado, sem nenhum efeito visível para quem está fazendo deploy —
usado para descobrir o real impacto da regra antes de ativá-la.
<strong>warn</strong> mostra um aviso no próprio <code>kubectl apply</code>
mas ainda aceita a operação, dando aos times a chance de corrigir por
conta própria antes que vire bloqueio. <strong>enforce</strong>
finalmente bloqueia — e só deveria ser ativado depois que os estágios de
audit e warn já estiverem "limpos" (sem violações restantes conhecidas).
Pular direto para enforce é o anti-padrão mais citado na seção 13.</p>

<h3>8. Webhook em produção: por que um serviço externo pode derrubar o cluster inteiro</h3>
<p>Um webhook de admission mal configurado tem um poder incomum: se o
apiserver depende da resposta dele e o webhook está fora do ar, TODO
<code>kubectl apply</code> no cluster pode ficar pendurado esperando uma
resposta que nunca chega — um único serviço externo com poder de travar
o plano de controle inteiro. As mitigações práticas: usar
<code>failurePolicy: Ignore</code> para webhooks não-críticos, onde uma
falha do webhook não deveria bloquear operações normais;
<code>failurePolicy: Fail</code> só para os realmente críticos de
segurança, mas SOMENTE com alta disponibilidade garantida (3+ réplicas,
PodDisruptionBudget) — sem essa garantia, "fail closed" vira "cluster
travado" na primeira instabilidade do webhook. Um
<code>timeoutSeconds</code> curto (5 segundos ou menos) evita que um
webhook lento atrase o cluster inteiro mesmo estando tecnicamente no ar.
<code>namespaceSelector</code> deve excluir explicitamente
<code>kube-system</code> e o próprio namespace do webhook — validar a si
mesmo cria uma dependência circular perigosa. Ter um runbook de
"desligar em emergência" com script pré-aprovado para remover o webhook
rapidamente é o kill switch que evita um incidente de webhook virar um
incidente de cluster inteiro fora do ar. E monitorar latência e taxa de
erro do próprio webhook trata a política de admission como o
componente crítico de infraestrutura que ela de fato é.</p>

<h3>9. Ordem de execução: por que mutating sempre roda antes de validating</h3>
<p>Todos os webhooks mutating rodam primeiro — pode haver vários ao
mesmo tempo (o injetor do Istio, o injetor do Vault Agent, defaults
diversos), e a ORDEM entre eles não é garantida como determinística. A
implicação prática é escrever políticas de mutação IDEMPOTENTES —
aplicar a mesma mutação duas vezes deveria produzir o mesmo resultado
que aplicá-la uma vez, já que você não controla se outro webhook mutating
já alterou o objeto antes do seu rodar. Só depois de TODOS os mutating
terminarem é que os webhooks validating entram em ação, e eles operam
sobre o objeto JÁ MUTADO — o que vai para o etcd é o resultado
pós-mutação, não o request original enviado pelo usuário.</p>

<h3>10. Verificação de assinatura: garantir proveniência, não só conteúdo</h3>
<p>O Sigstore Policy Controller é um admission webhook especializado em
validar que uma imagem foi assinada por uma fonte autorizada antes de
permitir que ela rode:</p>
<pre><code>apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata: { name: signed-by-team }
spec:
  images:
  - glob: ghcr.io/myorg/**
  authorities:
  - keyless:
      url: https://fulcio.sigstore.dev
      identities:
      - issuer: https://token.actions.githubusercontent.com
        subject: https://github.com/myorg/repo/.github/workflows/release.yml@refs/heads/main</code></pre>
<p>A assinatura "keyless" (sem par de chaves gerenciado manualmente) usa
identidade do próprio workflow de CI como prova — o efeito prático é que
um pod só roda se a imagem foi construída e assinada EXATAMENTE pelo
workflow de release autorizado daquele repositório específico, fechando
o vetor de alguém publicar uma imagem com o mesmo nome a partir de outro
lugar. Combinado com SBOM e atestações SLSA (vistas na Fase 4), isso
constitui uma cadeia de supply chain verificável de ponta a ponta, não
apenas confiança implícita no nome do registry.</p>

<h3>11. Observabilidade das próprias políticas: saber o que está sendo bloqueado, e onde</h3>
<p>Kyverno gera automaticamente objetos <code>PolicyReport</code> (CRDs)
documentando cada violação encontrada — uma fonte estruturada e
consultável, em vez de vasculhar logs de texto livre do apiserver.
Gatekeeper expõe métricas Prometheus nativas: quantas constraints foram
violadas, qual a latência de avaliação de cada política. Encaminhar isso
para Grafana ou um SIEM, e agregar por namespace, revela rapidamente
"qual time acumula mais violações pendentes" — uma visão que orienta
onde investir esforço de correção primeiro, em vez de tratar todas as
violações como igualmente urgentes.</p>

<h3>12. O limite fundamental de admission: ele nunca vê o que acontece depois</h3>
<p>Admission é inteiramente PREVENTIVO — atua uma única vez, no momento
em que o recurso é criado ou atualizado, e nunca mais depois disso. Um
pod que passou por todas as validações e foi aprovado ainda pode se
comportar mal em runtime: um processo comprometido tentando escalar
privilégio, um binário tentando exfiltrar dados, um comportamento
completamente diferente do que a configuração estática sugeria. Nenhuma
política de admission enxerga isso, porque o momento de avaliação já
passou. É exatamente a lacuna que Falco e Tetragon (aula de Runtime
Security) preenchem — observando comportamento real do processo em
execução, não apenas a configuração declarada no momento da criação.</p>

<h3>13. Cinco anti-padrões que sabotam a adoção de admission policies</h3>
<ul>
<li><strong>Deploy direto em modo enforce</strong>: o time atualiza o
repositório, o deploy falha sem aviso prévio, e a reação natural é
"desliguem essa política" em vez de corrigir o problema real.</li>
<li><strong>Webhook único, sem alta disponibilidade</strong>: o cluster
inteiro fica refém de um único ponto de falha para toda operação de
admissão.</li>
<li><strong>Política gigante e ambígua</strong>: regras difíceis de
entender geram erros de rejeição confusos, e o time aprende a ignorar a
mensagem em vez de corrigir a causa.</li>
<li><strong>Sem mensagem clara de correção</strong>: um "denied" genérico
não diz COMO consertar — incluir um link para o runbook relevante na
própria mensagem de rejeição economiza idas e vindas.</li>
<li><strong>Política só valida o manifesto final, não o Helm chart
subjacente</strong>: o Helm aplica a release normalmente, a admission
rejeita o resultado, e a release fica num estado corrompido pela metade
— pior do que rejeitar antes de qualquer coisa ser tentada.</li>
</ul>

<h3>14. Roadmap pragmático: da instalação ao enforcement completo</h3>
<ol>
<li>Habilitar PSS restricted nos namespaces de produção (aula de
Hardening) como base antes de qualquer policy customizada.</li>
<li>Instalar Kyverno (caminho de menor atrito) ou Gatekeeper, conforme a
complexidade de regra que o time já antecipa precisar.</li>
<li>Aplicar de 5 a 10 políticas básicas em modo <em>audit</em> primeiro,
nunca direto em enforce.</li>
<li>Compartilhar um relatório semanal de violações com os times
afetados, dando visibilidade antes de qualquer bloqueio.</li>
<li>Promover para <em>warn</em> depois de aproximadamente duas semanas de
dados de audit.</li>
<li>Promover para <em>enforce</em> só depois de mais duas semanas em
warn, com as violações conhecidas já corrigidas.</li>
<li>Integrar verificação de assinatura de imagem como próxima camada.</li>
<li>Expandir com políticas específicas do domínio da própria
organização, construídas sobre a base já validada.</li>
</ol>"""
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
                """<h3>1. Os cinco princípios que separam experimento de vandalismo</h3>
<p>Chaos engineering não é "quebrar coisas para ver o que acontece" — é
um método científico aplicado a sistemas em produção, com cinco passos
que, pulados, transformam o experimento em teatro sem valor real:</p>
<ol>
<li><strong>Defina o estado estável (steady state)</strong>: uma métrica
MENSURÁVEL de saúde do sistema — taxa de sucesso de requisições, p99 de
latência, taxa de erro. Sem essa linha de base numérica, não há como
distinguir "o experimento causou uma regressão real" de "sempre foi
assim" — a comparação simplesmente não existe.</li>
<li><strong>Levante uma hipótese falsificável</strong>: "matar 1 pod web
não impacta o SLI" é uma afirmação que pode ser refutada pelo próprio
experimento. "Vamos ver o que acontece" não é hipótese — é ausência de
uma pergunta, e sem pergunta não há aprendizado direcionado, só
observação passiva.</li>
<li><strong>Introduza eventos do mundo real</strong>: latência de rede,
perda de uma zona inteira, corrupção de cache, certificado expirado — as
falhas que REALMENTE acontecem em produção, não falhas artificiais que
nunca ocorreriam sozinhas.</li>
<li><strong>Limite o raio de impacto (blast radius)</strong>: comece
minúsculo — 1 pod, 1 namespace, 1 região — e tenha um kill switch capaz
de interromper tudo instantaneamente. É a diferença entre um experimento
controlado e um incidente autoinduzido.</li>
<li><strong>Aprenda e aja</strong>: um experimento que revela uma falha
mas não gera nenhuma correção concreta depois é teatro — a validação só
tem valor se alguém de fato fecha o buraco encontrado.</li>
</ol>

<h3>2. Steady state na prática: o que faz uma métrica boa ou ruim</h3>
<p>Uma métrica de estado estável precisa refletir o que o USUÁRIO sente,
não o que é fácil de medir internamente. "p99 de latência abaixo de
500ms na rota /checkout" e "taxa de sucesso acima de 99,5%" são boas
porque conectam diretamente a uma experiência real — se o experimento
degradar qualquer uma delas, você sabe que algo que importa quebrou.
"CPU baixa" e "logs sem erro" são más métricas para esse propósito: CPU
baixa não diz nada sobre se o usuário está recebendo respostas corretas
(um sistema travado também tem CPU baixa), e logs "sem erro" só provam
que ninguém logou o erro — não que ele não aconteceu.</p>

<h3>3. Três categorias de experimento, três tipos de fraqueza</h3>
<p>Experimentos de <strong>resiliência</strong> testam a infraestrutura
contra falhas de infraestrutura: matar pods, injetar latência de rede,
derrubar DNS, simular perda de uma zona de disponibilidade inteira,
falhar o banco primário, esfriar o cache. Experimentos de
<strong>segurança</strong> testam os CONTROLES defensivos contra ataques
simulados: vazamento de credencial proposital, tentativa de exfiltração
de dados, comprometimento simulado de um pod, tentativa de fuga de
container. Experimentos <strong>operacionais</strong> testam o TIME, não
o sistema: derrubar o canal de paginação principal (a secundária
funciona?), tirar do ar quem está de plantão (o próximo da escala
responde?), forçar alguém a agir sem o runbook à mão (o improviso
aguenta?). As três categorias respondem perguntas diferentes — um
programa maduro de chaos engineering cobre as três, não só a mais fácil
de automatizar.</p>

<h3>4. O ecossistema de ferramentas, por categoria de uso</h3>
<p>Para clusters Kubernetes, <strong>Chaos Mesh</strong> (projeto CNCF)
expõe cada tipo de falha como um CRD nativo — <code>PodChaos</code>,
<code>NetworkChaos</code>, <code>IOChaos</code>, <code>KernelChaos</code>,
<code>TimeChaos</code> — o que significa versionar experimentos em Git do
mesmo jeito que qualquer outro manifesto do cluster (visto nas seções 5 e
6). <strong>LitmusChaos</strong> é a alternativa CNCF equivalente, com um
hub de experimentos prontos para reaproveitar. Fora do Kubernetes, os
provedores de nuvem têm serviços dedicados —
<strong>AWS Fault Injection Simulator</strong> para EC2/ECS/EKS/RDS,
<strong>Azure Chaos Studio</strong> e equivalentes na GCP — que injetam
falha diretamente na camada de infraestrutura gerenciada, sem precisar de
um agente rodando dentro do cluster. <strong>Gremlin</strong> é a opção
comercial multi-cloud mais madura do mercado.
<strong>ChaosMonkey/Simian Army</strong> da Netflix foi pioneiro (2010) e
inspirou toda essa categoria de ferramenta.
<strong>ChaoSlingr</strong> tem foco específico em experimentos de
segurança, o tema central desta aula. <strong>Toxiproxy</strong>
(Shopify) é um proxy TCP simples que injeta latência e perda de pacote,
útil para reproduzir falhas de rede em ambiente de desenvolvimento local,
sem precisar de um cluster inteiro.</p>

<h3>5. Exemplo Chaos Mesh: matar pods aleatórios de forma agendada</h3>
<pre><code>apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata: { name: kill-web-pods, namespace: prod }
spec:
  action: pod-kill
  mode: one             # 1 pod por vez
  duration: "30s"
  selector:
    namespaces: [prod]
    labelSelectors:
      app: web
  scheduler:
    cron: "@every 10m"  # a cada 10 min, mata 1 pod web</code></pre>
<p>O <code>scheduler</code> com sintaxe de cron transforma esse
experimento em CONTÍNUO, não um evento único disparado manualmente — o
cluster passa a conviver com pods morrendo de forma imprevisível o tempo
todo, exatamente o tipo de estresse constante que expõe dependências
escondidas (um serviço que assume que o pod que ele chamou sempre estará
lá) muito mais cedo do que um teste isolado.</p>

<h3>6. Exemplo: latência de rede entre serviços, e o que perguntar depois</h3>
<pre><code>apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata: { name: db-slow }
spec:
  action: delay
  mode: all
  selector:
    namespaces: [prod]
    labelSelectors: { app: api }
  delay:
    latency: "100ms"
    correlation: "100"
    jitter: "10ms"
  direction: to
  target:
    selector:
      namespaces: [prod]
      labelSelectors: { app: postgres }
    mode: all
  duration: "10m"</code></pre>
<p>Injetar 100ms de latência artificial entre a API e o banco não é o
experimento em si — é o GATILHO para as perguntas que realmente importam:
o p99 sobe proporcionalmente ou desproporcionalmente (indicando um
gargalo escondido, como um pool de conexões pequeno demais)? Os circuit
breakers configurados realmente disparam nesse cenário, ou só existem no
papel? Usuários reais percebem erro, ou o sistema absorve a degradação
graciosamente? Os alertas configurados para "latência alta" disparam
NESSE momento específico, ou só disparariam com uma latência bem maior
que a testada?</p>

<h3>7. Game Day: o mesmo princípio científico, aplicado ao time</h3>
<p>Um Game Day é um cenário simulado — em produção controlada ou em sala
via tabletop — desenhado para testar o TIME, não só o sistema. O roteiro
segue a mesma lógica do método científico da seção 1: na fase
<strong>pre-game</strong>, um facilitador define hipótese, blast radius e
métricas, mas o time que vai responder NÃO conhece os detalhes
específicos — testar contra um roteiro conhecido de antemão não mede
nada real. No <strong>game start</strong>, a falha é injetada de verdade
(em staging) ou narrada (tabletop). A fase de <strong>detecção</strong>
mede o MTTD (mean time to detect): quanto tempo até o time perceber pelos
canais reais — alertas, dashboards, reclamação de cliente — sem dica
externa. A <strong>resposta</strong> mede o MTTR (mean time to recover):
quanto tempo até o runbook real ser aplicado e o problema resolvido. A
fase de <strong>recovery</strong> confirma que o estado estável definido
na hipótese voltou. O <strong>postmortem</strong> final captura o que
funcionou, o que falhou, e vira ação concreta. Os achados mais comuns em
Game Days reais são quase sempre os mesmos: alertas mal-configurados
(dispararam tarde, ou nunca dispararam), runbooks desatualizados
(referenciam um sistema que já mudou), dependências escondidas (ninguém
sabia que o serviço X dependia do Y) e caminhos de escalonamento que
simplesmente não existem quando alguém precisa deles.</p>

<h3>8. Chaos de segurança: validar o controle, não só a infraestrutura</h3>
<p>A diferença central de chaos de SEGURANÇA para chaos de resiliência é
que aqui o alvo do experimento é um CONTROLE DEFENSIVO, não um componente
de infraestrutura. "Esquecer" deliberadamente uma chave AWS num
repositório de teste público mede três tempos de resposta em cadeia:
quanto até o scanner de segredo do próprio CI alertar, quanto até o
GitHub revogar automaticamente, e quanto até o SOC perceber via
CloudTrail que aquela credencial foi usada de algum lugar inesperado —
cada camada de defesa testada isoladamente. Simular exfiltração fazendo
um pod chamar um domínio "canário" (controlado, para observação) testa
se o DLP ou o SIEM realmente detectam tráfego de saída suspeito, ou só
detectariam num relatório teórico. Simular uma tentativa de escalada de
privilégio (um <code>setuid</code> dentro de um container, por exemplo)
testa diretamente se o Falco (ou equivalente) de fato gera o alerta que
deveria. Introduzir uma ServiceAccount com <code>cluster-admin</code>
temporário testa se a auditoria de RBAC detecta a anomalia. E uma imagem
com um cryptominer disfarçado testa se o scan de imagem e a admission
policy (vistos na aula de Admission Controllers) realmente bloqueiam
antes do deploy, não só teoricamente.</p>

<h3>9. Chaos em produção: sim, mas com um kill switch testado antes de precisar dele</h3>
<p>Rodar chaos engineering direto em produção é seguro quando seguido de
uma progressão: comece em desenvolvimento e staging até ganhar confiança
no comportamento das ferramentas e nos limites de blast radius. Só então
avance para um Game Day isolado em produção, com janela de tempo
COMUNICADA a todos os stakeholders relevantes ("no dia X às Y, vamos
derrubar uma zona inteira na região Z por 15 minutos"). O kill switch —
um comando único capaz de interromper o experimento inteiro
instantaneamente — precisa ser TESTADO antes do primeiro experimento
real, não só existir na teoria; um kill switch que nunca foi acionado é
tão confiável quanto um backup que nunca foi restaurado. Tenha sempre um
plano B para o cenário em que o experimento vira um incidente de
verdade. A Netflix opera <strong>chaos contínuo</strong> em produção há
anos — o estágio final de maturidade, onde o blast radius é pequeno o
suficiente para rodar o tempo todo sem risco relevante.</p>

<h3>10. Métricas: como provar que o programa de chaos vale o investimento</h3>
<p>MTTD e MTTR (definidos na seção 7) são as métricas centrais — quanto
menores ao longo do tempo, mais rápido o time detecta e se recupera de
problemas reais, não só simulados. "Findings por experimento" conta
descobertas concretas: bugs em runbook, alertas que deveriam ter tocado e
não tocaram, dependências escondidas reveladas. "Action items
completados" mede se as descobertas realmente viram correção, ou só
ficam registradas e esquecidas (o anti-padrão da seção 12). A métrica
mais difícil de capturar — mas a justificativa final do programa inteiro
— é a redução de incidentes REAIS depois que o chaos engineering começou:
provar causalidade exige comparar períodos longos, mas é o número que
convence quem financia o programa de que ele vale o esforço.</p>

<h3>11. A pirâmide de maturidade: onde a maioria dos times deveria começar</h3>
<ol>
<li><strong>Tabletop exercises</strong>: cenário narrado em sala, sem
tocar em sistema nenhum. Fácil, sem risco, o ponto de partida certo para
qualquer time que nunca fez isso.</li>
<li><strong>Chaos manual em dev/staging</strong>: pequenas falhas
controladas, ainda longe de produção.</li>
<li><strong>Game days agendados em produção</strong>: janela comunicada,
blast radius limitado, mas já no ambiente real.</li>
<li><strong>Chaos contínuo em produção</strong> com blast radius pequeno
— falhas acontecendo o tempo todo, de forma automatizada e segura.</li>
<li><strong>Chaos como cultura</strong>: cada time mantém seus próprios
experimentos, sem depender de uma equipe central para rodá-los.</li>
</ol>
<p>Pular etapas — ir direto para chaos contínuo em produção sem nunca ter
feito um tabletop — costuma terminar no primeiro anti-padrão da seção
12: um blast radius grande demais na primeira tentativa, o time perde
confiança na prática inteira, e o programa morre antes de amadurecer.</p>

<h3>12. Cinco formas de o programa falhar antes de gerar valor</h3>
<ul>
<li><strong>Chaos sem hipótese</strong>: "vamos ver o que acontece" é
vandalismo, não experimento — sem uma pergunta específica, qualquer
resultado parece "interessante" mas não ensina nada acionável.</li>
<li><strong>Sem postmortem com ação concreta</strong>: o experimento
revela um buraco real, mas ninguém o fecha depois — a próxima rodada de
chaos vai encontrar o MESMO problema, e a organização não aprendeu
nada.</li>
<li><strong>Blast radius gigante na primeira tentativa</strong>: um
experimento mal calibrado que derruba mais do que deveria na estreia faz
o time perder confiança na prática inteira, e frequentemente mata o
programa antes dele amadurecer.</li>
<li><strong>Chaos sem coordenar com o SOC</strong>: se o time de segurança
não sabe que um experimento está em curso, os alertas reais que ele
dispara são descartados como "mais um teste" — inclusive quando, por
coincidência, um ataque de verdade acontece na mesma janela.</li>
<li><strong>Só resilience chaos, nunca security chaos</strong>: testar
exaustivamente a infraestrutura contra falha e nunca testar os controles
de defesa contra um atacante deixa metade do valor da prática inteira
sobre a mesa.</li>
</ul>"""
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
                """<h3>1. NIST SP 800-61: por que o framework é um ciclo, não uma lista</h3>
<p>O NIST estrutura resposta a incidente em quatro fases, e o detalhe
que muita gente perde é que a última fase ALIMENTA a primeira, fechando
um ciclo de melhoria contínua, não um checklist linear que termina no
"resolvido". <strong>Preparation</strong> é tudo que se faz ANTES do
incidente acontecer — runbooks escritos, treino praticado, ferramentas
já configuradas, contatos atualizados, acessos de emergência
("break-glass") prontos para uso. É sistematicamente a fase mais
subestimada, porque não produz resultado visível no curto prazo — e
justamente por isso é a que mais separa um time que responde em 10
minutos de um que leva 10 horas para o mesmo incidente.
<strong>Detection & Analysis</strong> cobre desde o alerta chegando até a
triagem: distinguir falso positivo de incidente real, determinar escopo
e severidade. <strong>Containment, Eradication & Recovery</strong> é a
fase de ação — limitar o avanço do problema, remover o que causou (um
artefato malicioso, uma configuração errada), restaurar o serviço.
<strong>Post-Incident Activity</strong> — o postmortem blameless (seção
7), os action items resultantes, atualização de runbook — é o que fecha
o ciclo, alimentando de volta a fase de Preparation com lições
aprendidas. Um time que pula essa última fase repete os mesmos
incidentes indefinidamente, porque nunca converte a experiência em
prevenção.</p>

<h3>2. Papéis num incidente: por que quem decide não deve tocar no teclado</h3>
<p>Em incidentes pequenos, uma pessoa acumula vários papéis sem problema.
Em incidentes grandes, separar os papéis deixa de ser organização e vira
necessidade: a pessoa que DECIDE não pode estar simultaneamente com "mãos
no teclado" executando ações, porque a atenção dividida entre coordenar e
executar é exatamente onde erros acontecem sob pressão. O
<strong>Incident Commander (IC)</strong> decide, coordena, aprova ações
de risco e mantém a visão geral da timeline — deliberadamente SEM mexer
em sistema nenhum, para manter a cabeça livre para decisão. A
<strong>Operação/Tech Lead</strong> é quem de fato executa as ações
técnicas aprovadas pelo IC. A função de <strong>Comunicação</strong> lida
com stakeholders internos, clientes e, se necessário, imprensa, mantendo
a status page atualizada — sem essa função dedicada, o IC acaba
respondendo pergunta de stakeholder no meio de uma decisão técnica
crítica. O <strong>Scribe</strong> registra a timeline em tempo real (uma
thread de Slack, um documento compartilhado) — sem esse registro
contemporâneo, o postmortem depende de memória reconstruída DEPOIS do
fato, sistematicamente menos precisa. Em incidentes de segurança, um
<strong>Security Lead</strong> dedicado preserva evidência forense e
coordena a investigação, uma responsabilidade distinta o suficiente da
resposta operacional geral para merecer papel próprio.</p>

<h3>3. Severidade: por que precisa estar definida antes das 3 da manhã</h3>
<p>Critérios de severidade servem a um propósito específico: eliminar a
decisão arbitrária no momento de maior estresse, quando o julgamento
humano está mais comprometido. <strong>SEV1</strong> — indisponibilidade
total ou exposição grave de dados, como produção fora do ar ou uma
violação confirmada — aciona pager 24/7 e comunicação imediata, sem
depender de alguém decidir "isso é grave o suficiente?" no calor do
momento. <strong>SEV2</strong> cobre degradação significativa (uma
região inteira fora, latência 5 vezes maior que o normal) com resposta
esperada em até uma hora. <strong>SEV3</strong> é um bug isolado ou
problema parcial, tratável em horário comercial normal. <strong>SEV4</strong>
é cosmético, baixa prioridade. Ter esses limiares documentados e
acordados ANTES do incidente é o que evita a situação onde duas pessoas
diferentes classificam o mesmo sintoma de forma completamente diferente
— um "chama todo mundo agora" contra um "vê amanhã" — só porque não
existia critério explícito para consultar.</p>

<h3>4. Comunicação: um canal dedicado, não o Slack pessoal de alguém</h3>
<p>Um canal específico por incidente
(<code>#inc-2026-04-25-auth-down</code>) preserva contexto e auditoria
que uma DM pessoal nunca teria — qualquer pessoa que entre depois consegue
ler o histórico completo, e a organização mantém um registro pesquisável
de como cada incidente foi conduzido. Uma bridge de voz (Zoom, Meet)
serve para discussão rápida que seria lenta demais por texto. Uma status
page pública, atualizada periodicamente mesmo sem novidade real,
resolve um problema psicológico conhecido: silêncio durante um incidente
é interpretado por clientes como pior sinal do que uma atualização
honesta dizendo "ainda investigando" — a incerteza incomoda mais que a
má notícia clara. Um template de atualização recorrente ajuda a manter
esse ritmo sem reinventar a redação a cada vez:</p>
<pre><code>UPDATE 14:30 UTC: continuamos investigando latência elevada
no checkout. Times de pagamento e infra envolvidos. Próximo update: 15:00.</code></pre>
<p>Uma matriz de escalonamento — documentando quem chamar quando o IC não
responde, em que ponto o nível executivo precisa ser informado, quando o
jurídico precisa entrar — evita que essas decisões sejam inventadas na
hora, sob pressão, pela primeira vez.</p>

<h3>5. Containment: parar o sangramento antes de investigar a fundo</h3>
<p>Containment de curto prazo tem um objetivo único: interromper o dano
em andamento o mais rápido possível, mesmo antes de entender a causa
completa — isolar um pod ou host comprometido (via NetworkPolicy ou
taint), revogar uma credencial suspeita (matar um JWT, rotacionar uma
chave), desligar um feature toggle que está causando o problema, ou
bloquear um IP malicioso no WAF. Containment de longo prazo já olha para
a erradicação que vem depois: tirar um snapshot ou preservar evidência
forense ANTES de destruir qualquer coisa (uma vez destruído, não há como
investigar depois), identificar IOCs — indicadores de comprometimento
como IPs, hashes de arquivo, domínios — e mapear a real extensão do
comprometimento, porque agir sobre um escopo menor do que o real deixa
persistência escondida que reaparece depois.</p>

<h3>6. Eradication e Recovery: por que rotacionar "só o que foi comprometido" não basta</h3>
<p>Reconstruir imagens e containers do zero, em vez de "limpar" os
existentes, garante que nenhum artefato malicioso sobreviva escondido —
limpeza manual de um sistema potencialmente comprometido é uma aposta,
reconstrução do zero é uma garantia. Rotacionar TODOS os segredos dentro
do escopo afetado — não só os comprovadamente vazados — reconhece uma
limitação real de investigação: provar que uma credencial NÃO foi
comprometida costuma ser mais difícil e mais lento do que simplesmente
trocá-la. Aplicar o patch da vulnerabilidade raiz fecha a porta que
permitiu o incidente originalmente — sem isso, o mesmo vetor continua
disponível para o próximo ataque. Restaurar de backup quando há
destruição ou ransomware exige que o backup já tenha sido testado antes
(a aula de backup da Fase 3 cobre por quê). Validar que o serviço voltou
ao estado estável antes de declarar o incidente encerrado evita reabrir
o mesmo incidente horas depois. E monitoramento intensificado por dias
após o incidente detecta uma segunda onda ou uma tentativa de retorno do
mesmo atacante, que raramente desiste na primeira tentativa bloqueada.</p>

<h3>7. Postmortem blameless: mudar a pergunta muda o que se aprende</h3>
<p>A diferença entre um postmortem que gera melhoria real e um que só
distribui culpa está na pergunta que ele faz: "como o SISTEMA permitiu
que um erro humano causasse impacto?" em vez de "quem errou?". A segunda
pergunta produz defensividade e informação escondida na próxima vez; a
primeira produz correção estrutural que previne a PRÓXIMA pessoa de
cometer o mesmo erro, porque o sistema — não a pessoa — é o alvo da
correção. Um postmortem completo tem sumário executivo de 2-3 linhas
(para quem não vai ler o documento inteiro), impacto quantificado (tempo
de duração, percentual de usuários afetados, valor perdido, dados
expostos), uma timeline detalhada com timestamp de cada ação, análise de
causa raiz (5 Whys ou diagrama de espinha de peixe), o que funcionou bem
(seção frequentemente esquecida, mas importante para preservar práticas
que já funcionam), o que pode melhorar, e action items — cada um com
dono, prazo e ticket rastreável. Sem essa última parte, o documento é só
uma narrativa bem escrita que não muda nada na prática. Um exemplo real
de "5 Whys" mostra como a técnica desce da superfície até a causa
estrutural:</p>
<pre><code>Sintoma: API ficou 30 min fora.
Por quê? Pod web entrou em CrashLoopBackOff.
Por quê? Liveness probe começou a falhar quando DB ficou lento.
Por quê? Probe fazia query no DB (acoplamento ruim).
Por quê? Template antigo da empresa, nunca questionado.
Por quê? Nenhuma revisão de templates desde 2 anos.
Action item: revisar todos templates de Deployment para liveness mais leve.</code></pre>
<p>Note que a causa raiz de verdade não é "o probe falhou" — é "ninguém
revisa templates há dois anos", um problema de PROCESSO que a
correção técnica pontual (trocar a liveness probe) não resolveria
sozinha em outros templates igualmente antigos.</p>

<h3>8. SOAR: automatizar a parte repetitiva da resposta, não a decisão</h3>
<p>SOAR (Security Orchestration, Automation and Response) automatiza os
passos MECÂNICOS e repetitivos de uma resposta, deixando a decisão final
para um humano: quando um alerta de um tipo conhecido dispara, o playbook
automaticamente enriquece o alerta (consulta o IP em bases de threat
intel, faz GeoIP, WHOIS), verifica se bate com um padrão de falso
positivo já conhecido, aplica containment imediato se apropriado
(bloquear IP no WAF, isolar o pod), abre um ticket, notifica o canal
certo — e só então espera uma pessoa decidir se o incidente precisa
escalar. O ganho não é eliminar o humano da resposta, é eliminar o tempo
gasto em passos que uma máquina executa em segundos e um humano levaria
minutos repetindo manualmente toda vez. Splunk SOAR (antigo Phantom),
Tines, n8n, Shuffle e Demisto são as ferramentas mais usadas nessa
categoria.</p>

<h3>9. Threat intelligence: defesa que se beneficia de compartilhamento</h3>
<p>Um IOC (Indicator of Compromise) é qualquer sinal observável que
aponta para atividade maliciosa — hash de um arquivo malicioso, IP de um
servidor de comando-e-controle, domínio suspeito, user agent incomum,
ou um padrão de comportamento. STIX/TAXII são os padrões técnicos que
permitem trocar esses indicadores entre organizações de forma
estruturada; MISP é a plataforma open-source mais usada para operar
essa troca; ISACs (Information Sharing and Analysis Centers) organizam
esse compartilhamento por setor — o FS-ISAC, por exemplo, é específico
do setor financeiro. A lógica de compartilhar IOCs com pares é uma forma
de defesa coletiva: um ataque que já foi identificado por outra empresa
do setor deixa de ser "desconhecido" para quem recebe o indicador a
tempo — e o mesmo vale ao receber de volta.</p>

<h3>10. MITRE ATT&CK e D3FEND: um vocabulário comum para ataque e defesa</h3>
<p>ATT&CK cataloga táticas e técnicas reais que adversários usam,
organizadas de forma padronizada — em vez de descrever um ataque em
prosa livre ("o invasor conseguiu se mover lateralmente de um jeito
esperto"), um postmortem pode mapear cada passo observado para uma
técnica ATT&CK específica, tornando o relato comparável entre incidentes
diferentes e entre organizações diferentes. D3FEND é o espelho
defensivo: contramedidas específicas mapeadas contra cada técnica do
ATT&CK. Na fase de Preparation, comparar quais técnicas do ATT&CK a
organização JÁ cobre com contramedidas do D3FEND revela lacunas de
defesa de forma sistemática, em vez de depender de intuição sobre "o que
ainda não cobrimos".</p>

<h3>11. Tabletop exercises: praticar sem nenhum risco técnico</h3>
<p>Um tabletop é simulação puramente verbal — nada é tocado em sistema
real. Um facilitador descreve um cenário ("às 3h da manhã, um alerta
indica vazamento de 10GB para um IP suspeito"), os participantes
descrevem o que fariam passo a passo, e o facilitador injeta
complicações no meio ("mas o oncall principal está de férias e o
secundário não responde") para testar o plano B que ninguém tinha
pensado. A discussão que emerge revela buracos reais em runbook,
comunicação e escalonamento — pelo mesmo custo de uma reunião de uma
hora, sem nenhum risco de causar um incidente de verdade tentando
simulá-lo. É a prática de menor custo e maior retorno desta aula inteira,
e por isso vale fazer com frequência trimestral, não uma vez por ano.</p>

<h3>12. Cultura de postmortem: o trabalho mais difícil de sustentar</h3>
<p>Cultura blameless não é uma política escrita, é um comportamento
observável ao longo do tempo — e é sistematicamente o elemento mais
difícil de instalar numa organização, porque contraria o instinto humano
de procurar quem é responsável quando algo dá errado. Sinais reais de que
a cultura está funcionando: escrever um postmortem não é visto como
punição por quem escreve; postmortems são compartilhados abertamente
dentro da empresa, inclusive com o nível executivo, em vez de arquivados
discretamente; a organização discute "near misses" — incidentes que
quase aconteceram mas foram evitados — com a mesma seriedade de
incidentes reais, porque a diferença entre os dois é frequentemente
sorte, não competência; action items são de fato rastreados até
completar, não só listados e esquecidos; e não há caça a culpado — a
premissa de partida é que cada pessoa agiu com a melhor decisão possível
dada a informação que tinha NO MOMENTO, não com o benefício de
retrospecto.</p>

<h3>13. As métricas que provam se a resposta está melhorando</h3>
<p>MTTD mede tempo até detecção — quanto maior, mais tempo um atacante
ou uma falha tem para causar dano antes de alguém perceber; a meta
realista é minutos, não horas. MTTA mede tempo até reconhecimento (o
"ack" de quem recebe o alerta do pager) — meta abaixo de 5 minutos,
porque um alerta não reconhecido é equivalente a nenhum alerta. MTTR mede
tempo até recuperação completa — a meta varia por severidade, mas a
tendência ao longo do tempo importa mais que o número absoluto de um
incidente isolado. Frequência de incidentes por severidade revela se o
sistema está ficando mais ou menos frágil ao longo dos meses. Action
items completados mede se o ciclo de melhoria (seção 1) está de fato
fechando, não só gerando documento. E repetição de causa-raiz — a MESMA
falha aparecendo pela terceira vez — é o sinal mais claro de um problema
sistêmico que nenhuma correção pontual resolveu de verdade.</p>

<h3>14. Sete anti-padrões que garantem incidentes mais longos</h3>
<ul>
<li><strong>Sem runbook</strong>: cada incidente vira improviso do zero,
às 3 da manhã, sob a pior condição possível para pensar com clareza.</li>
<li><strong>Runbook nunca testado</strong>: documento escrito e nunca
exercitado tem aproximadamente 50% de chance de estar desatualizado ou
errado exatamente quando é preciso — a mesma lógica de um backup nunca
restaurado.</li>
<li><strong>Comunicação por DM ou WhatsApp pessoal</strong>: nenhuma
auditoria, nenhum histórico pesquisável, contexto perdido assim que a
conversa rola para baixo.</li>
<li><strong>IC com as mãos no teclado</strong>: ninguém sobra para
coordenar a visão geral enquanto essa pessoa está focada em executar uma
ação técnica específica.</li>
<li><strong>Postmortem caçando culpado</strong>: garante que a próxima
pessoa esconda informação relevante em vez de compartilhá-la
abertamente, exatamente o oposto do que investigação eficaz precisa.</li>
<li><strong>Action items sem dono nem prazo</strong>: viram uma lista de
boas intenções que nunca se materializa em correção real.</li>
<li><strong>Severidade decidida arbitrariamente</strong>: o mesmo tipo de
sintoma classificado como SEV1 numa ocasião e "vemos amanhã" noutra, só
porque não existia critério documentado para consultar.</li>
</ul>

<h3>15. Roadmap pragmático: da ausência total de processo à maturidade</h3>
<ol>
<li>Definir critérios de severidade explícitos, documentados, acessíveis
a qualquer pessoa que precise classificar um incidente às 3h da manhã.</li>
<li>Implementar canal de incidente, status page e matriz de
escalonamento antes do próximo incidente acontecer, não durante.</li>
<li>Escrever runbooks para os cinco cenários mais prováveis de acontecer
— não tentar cobrir tudo de uma vez.</li>
<li>Rodar um tabletop exercise mensal para exercitar esses runbooks sem
risco.</li>
<li>Depois de todo incidente real, produzir postmortem dentro de 5 dias
úteis — atraso demais e os detalhes já foram esquecidos.</li>
<li>Automatizar via SOAR os playbooks que se repetem com maior
frequência, priorizando por volume observado, não por achismo.</li>
<li>Rodar Game Days trimestrais combinando chaos engineering (aula
anterior) com prática de resposta real.</li>
</ol>"""
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
                """<h3>1. Frameworks: por que existem tantos, e qual se aplica a você</h3>
<p>Cada framework de compliance nasceu para resolver um problema
específico, e a maioria das empresas precisa de mais de um simultaneamente.
A <strong>LGPD</strong> (Lei Geral de Proteção de Dados, Brasil, 2018)
regula como dados pessoais são tratados — princípios, bases legais,
direitos do titular, obrigações do controlador/operador — com multas que
chegam a R$50 milhões por infração ou 2% do faturamento, o suficiente para
tornar não-conformidade um risco financeiro real, não só reputacional. A
<strong>GDPR</strong> é o equivalente europeu, com multas ainda maiores
(4% do faturamento global ou €20M) e se aplica a qualquer empresa que
trate dados de cidadãos da UE, mesmo sem sede lá. <strong>ISO 27001</strong>
certifica um Sistema de Gestão de Segurança da Informação inteiro (93
controles no Anexo A), renovado por auditor acreditado anualmente — é
sobre PROCESSO de segurança, não uma lei específica. <strong>SOC 2</strong>
é o padrão de fato para SaaS B2B nos EUA, com dois níveis: Type I avalia o
DESENHO dos controles num instante; Type II avalia se eles realmente
FUNCIONARAM ao longo de 6+ meses — o segundo é o que clientes enterprise
de verdade exigem, porque prova operação real, não intenção no papel.
<strong>PCI DSS</strong> se aplica a quem toca dado de cartão, mesmo
processando via Stripe — o escopo de controle reduz, mas não some.
<strong>HIPAA</strong> cobre dados de saúde nos EUA, <strong>NIST CSF</strong>
organiza práticas de segurança em cinco funções
(Identify/Protect/Detect/Respond/Recover) de forma voluntária, e
<strong>FedRAMP</strong> é o padrão para vender à nuvem do governo
americano.</p>

<h3>2. Os dez princípios da LGPD: o que cada um proíbe na prática</h3>
<p>Cada princípio da LGPD existe para bloquear um comportamento
específico que a lei considera abusivo. <strong>Finalidade</strong> exige
que o tratamento tenha um propósito legítimo, específico e explícito —
"para melhorar nossos serviços" é vago demais para servir de base legal
real, porque não delimita o que de fato será feito com o dado.
<strong>Adequação</strong> exige que o tratamento seja compatível com
essa finalidade declarada — coletar CPF "para enviar newsletter" não
seria adequado. <strong>Necessidade</strong> proíbe coletar mais do que
o mínimo indispensável: se um nome resolve, pedir CPF é excesso.
<strong>Livre acesso</strong> garante ao titular consulta gratuita aos
próprios dados. <strong>Qualidade</strong> exige dados exatos e
atualizados. <strong>Transparência</strong> exige que a informação sobre
o tratamento seja acessível, não escondida em letra miúda.
<strong>Segurança</strong> e <strong>prevenção</strong> exigem medidas
técnicas e administrativas concretas — não intenção, mas controle real.
<strong>Não-discriminação</strong> proíbe usar dados para fins
discriminatórios (negar crédito por CEP, por exemplo). E
<strong>responsabilização</strong> (accountability) exige que a empresa
consiga DEMONSTRAR que adotou essas medidas, não apenas afirmar que
adotou — é o princípio que torna toda a auditoria e evidência do resto
desta aula obrigatória, não opcional.</p>

<h3>3. Bases legais: por que todo tratamento precisa de uma, documentada</h3>
<p>O artigo 7º da LGPD lista dez bases legais possíveis — consentimento,
cumprimento de obrigação legal, execução de contrato, legítimo interesse
(entre outras) — e a regra prática que decorre disso é simples de
enunciar e trabalhosa de cumprir: TODO tratamento de dado pessoal precisa
mapear para uma dessas bases, documentada num inventário de tratamentos.
Sem esse mapeamento, uma empresa não consegue responder à pergunta mais
básica de uma fiscalização — "por que vocês têm este dado?" — com uma
base legal específica, só com justificativas genéricas que não
sobrevivem a uma auditoria real.</p>

<h3>4. Os papéis da LGPD, e por que confundi-los é um erro caro</h3>
<p>O <strong>controlador</strong> é quem DECIDE o tratamento — a empresa
que coleta o dado para seu próprio propósito. O <strong>operador</strong>
processa em nome do controlador (a AWS guardando seus dados, um
fornecedor de e-mail transacional) — e o operador não decide finalidade,
só executa. Essa distinção importa porque a responsabilidade legal recai
principalmente sobre o controlador, mesmo quando o incidente acontece na
infraestrutura do operador — é por isso que o DPA (seção 12) com cada
operador não é burocracia, é a documentação que define quem responde por
quê. O <strong>DPO/Encarregado</strong> é o ponto de contato oficial com
a ANPD (Autoridade Nacional de Proteção de Dados) e com os titulares —
nome e contato divulgados publicamente, não um cargo interno anônimo. O
<strong>titular</strong> é a pessoa física a quem os dados se referem —
o centro de todo o resto da lei.</p>

<h3>5. Os nove direitos do titular, e como operacionalizá-los sem virar processo manual</h3>
<p>O artigo 18 garante ao titular confirmar a existência de tratamento,
acessar seus dados, corrigi-los, pedir anonimização/bloqueio/eliminação,
portar os dados para outro serviço, eliminar dados tratados por
consentimento, saber com quem o controlador compartilhou seus dados,
saber as consequências de negar consentimento, e revogar consentimento a
qualquer momento. Tratar cada pedido manualmente — um e-mail, uma
planilha, um funcionário caçando dados em sistemas diferentes — não
escala além de algumas dezenas de solicitações; a resposta operacional é
um portal de privacidade ("Privacy Center") com fluxo automatizado para
DSAR (Data Subject Access Request), já que o PRAZO legal é de 15 dias —
sem automação, esse prazo se torna sistematicamente inviável assim que o
volume de solicitações cresce.</p>

<h3>6. RIPD/DPIA: avaliar o risco antes de tratar, não depois do incidente</h3>
<p>O Relatório de Impacto à Proteção de Dados (RIPD na LGPD, DPIA na
GDPR) é obrigatório quando o tratamento envolve risco alto — dado de
categoria sensível, decisão automatizada sobre pessoas, dados de
menores, monitoramento sistemático. O documento descreve o tratamento, a
finalidade, as categorias de dado e titular envolvidas, avalia
necessidade e proporcionalidade, identifica riscos com probabilidade e
impacto, define medidas de mitigação, e recebe parecer formal do DPO. A
lógica por trás da exigência é preventiva: forçar a avaliação de risco
ANTES do tratamento começar, não depois de um vazamento revelar que o
risco nunca tinha sido pensado.</p>

<h3>7. Continuous compliance: aplicar princípios de DevOps a auditoria</h3>
<p>O problema que continuous compliance resolve é estrutural: auditoria
anual tradicional produz um retrato do sistema em UM instante do ano, que
pode já estar desatualizado no dia seguinte — e o processo de coletar
evidência manualmente (prints de tela, planilhas, e-mails de confirmação)
consome semanas de trabalho repetitivo e ainda assim produz um documento
estático. A alternativa aplica a mesma lógica de infraestrutura-como-código
à conformidade: cada controle vira uma REGRA avaliável automaticamente
("todo bucket S3 deve ser privado"); o ambiente real é avaliado
CONTINUAMENTE contra essas regras, não uma vez por ano; a evidência
(logs, exports, screenshots automáticos) é gerada pelo próprio sistema, não
por um humano caçando prova; e é armazenada em local imutável (WORM —
Write Once Read Many). O resultado prático: quando o auditor chega, ele
CONSULTA a plataforma de compliance diretamente, em vez de esperar a
empresa reunir evidência sob pressão — a auditoria deixa de ser um evento
traumático de meses e vira um relatório quase instantâneo do que já
estava sendo medido o ano inteiro.</p>

<h3>8. O ecossistema de ferramentas de continuous compliance</h3>
<p><strong>AWS Config</strong>, <strong>Azure Policy</strong> e
<strong>GCP Organization Policies</strong> detectam desvio de
configuração nos próprios recursos de nuvem — um bucket que virou público
sem autorização, por exemplo, é sinalizado no momento em que a mudança
acontece, não só na próxima auditoria manual. <strong>Cloud Custodian</strong>
generaliza essa ideia com regras de policy E remediação automática em
YAML, funcionando através de múltiplas nuvens ao mesmo tempo.
<strong>Drata, Vanta, Sprinto, Tugboat Logic, Secureframe</strong> são
plataformas SaaS especializadas em coletar evidência de várias fontes
(cloud, GitHub, provedor de identidade, MDM, sistema de RH) automaticamente
e manter um dashboard mostrando o nível de conformidade em tempo real
contra um framework específico (SOC 2, ISO 27001) — o tipo de ferramenta
que transformou continuous compliance de conceito acadêmico em prática
comum para startups SaaS. <strong>OpenSCAP</strong> valida configuração
de Linux contra benchmarks SCAP padronizados; o <strong>Compliance
Operator</strong> do OpenShift aplica o mesmo princípio (via kube-bench e
policies) dentro de clusters Kubernetes. <strong>OneTrust</strong> e
<strong>BigID</strong> focam especificamente em privacidade e gestão de
risco de terceiros — rastrear quais fornecedores têm acesso a que tipo de
dado.</p>

<h3>9. AWS Config na prática: uma regra vira uma checagem contínua</h3>
<pre><code># habilitar regra: bucket S3 não pode ser público
$ aws configservice put-config-rule \\
  --config-rule '{
    "ConfigRuleName": "s3-bucket-public-read-prohibited",
    "Source": {
      "Owner": "AWS",
      "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
    }
  }'

# Conformance Pack: agrupa regras para frameworks
$ aws configservice put-conformance-pack \\
  --conformance-pack-name lgpd-baseline \\
  --template-s3-uri s3://my-bucket/lgpd-pack.yaml</code></pre>
<p>Uma vez habilitada, essa regra reavalia TODO bucket S3 da conta a cada
mudança de configuração, não só uma vez — um bucket que estava privado e
foi tornado público às 3h da manhã aparece como não-conforme no mesmo
momento, sem esperar o próximo ciclo de auditoria. Um "Conformance Pack"
agrupa dezenas de regras individuais sob o nome de um framework
específico (aqui, uma linha de base para LGPD), permitindo avaliar
"estamos conformes com X?" como uma pergunta única, em vez de checar regra
por regra manualmente.</p>

<h3>10. Evidência como código: tudo que a auditoria vai pedir, gerado sozinho</h3>
<p>A lista do que compõe evidência automatizada é longa porque cobre
áreas diferentes do sistema: saída de pipeline (lint, SAST, scan de
vulnerabilidade, DAST) prova que o código passou pelos controles
declarados; saída de kube-bench/kubescape prova hardening de cluster;
exports do AWS Config/Azure Policy provam conformidade de infraestrutura;
logs de IAM (CloudTrail, audit log do GCP) provam quem acessou o quê;
VPC Flow Logs provam padrão de tráfego de rede; reports de SCA/SBOM/scan
de imagem provam gestão de dependência; logs de PR aprovado provam
revisão de código; logs de LMS provam treinamento de funcionário; e
configuração de MDM prova se laptops estão criptografados e com tela
bloqueada. Armazenar tudo isso num bucket S3 com Object Lock (que impede
alteração ou exclusão mesmo por um administrador, dentro do período de
retenção) é o que torna a evidência CONFIÁVEL para um auditor — dado que
pode ter sido editado depois do fato não prova nada. O auditor recebe uma
URL pré-assinada com prazo de expiração, em vez de acesso direto e
permanente ao ambiente.</p>

<h3>11. Tagging: a base que faz uma policy de dados ser aplicável</h3>
<pre><code>tags:
  data_classification: pii  # public, internal, pii, phi, pci
  retention_days: 365
  owner: team-billing
  compliance: lgpd,sox
  env: prod</code></pre>
<p>Sem classificação consistente em CADA recurso, uma regra como "todo
recurso com dado PII deve ter criptografia habilitada, ser privado e ter
logging ativo" não tem como ser avaliada automaticamente — o Cloud
Custodian (ou equivalente) simplesmente não sabe QUAIS recursos essa
regra deveria checar. A tag <code>data_classification</code> é o que
converte uma política escrita em texto numa política executável: o
sistema filtra por essa tag e aplica a checagem só onde ela importa,
sem depender de um humano lembrando manualmente onde está cada tipo de
dado sensível.</p>

<h3>12. Práticas de dia a dia que sustentam compliance contínuo</h3>
<p>Manter o inventário de tratamentos atualizado é o que faz a seção 3
funcionar na prática, não só no papel. Criptografia em trânsito e em
repouso em TUDO — sem exceção "só neste sistema legado" — elimina uma
categoria inteira de risco de vazamento. Um portal DSAR automatizado
opera a seção 5. Treinamento anual de colaboradores reduz o vetor de
erro humano, historicamente a causa mais comum de incidente de dados.
Política de retenção automatizada (lifecycle policies que apagam dados
depois do prazo definido) evita acumular dado que nem deveria mais
existir — dado que não existe não pode vazar. Um DPA (Data Processing
Agreement) formal com cada operador documenta a distribuição de
responsabilidade da seção 4. Monitoramento de acesso a dado sensível
(DAM — Database Activity Monitoring — e trilhas de auditoria) detecta
uso indevido interno, não só ataque externo. E notificação de incidente
em até 72 horas é prazo legal na LGPD e na GDPR — sem um processo já
desenhado ANTES do incidente acontecer, esse prazo é praticamente
impossível de cumprir sob a pressão de uma crise real.</p>

<h3>13. SOC 2 em detalhe: os cinco critérios e o que Type II realmente prova</h3>
<p>Os cinco Trust Services Criteria são <strong>Security</strong>
(obrigatório em qualquer relatório SOC 2 — controles básicos de proteção
de sistema), <strong>Availability</strong> (SLAs de disponibilidade
cumpridos), <strong>Processing Integrity</strong> (o processamento
produz resultado correto e completo), <strong>Confidentiality</strong>
(dados marcados como confidenciais são protegidos como tal) e
<strong>Privacy</strong> (tratamento de dado pessoal, sobrepondo
parcialmente com LGPD/GDPR). A diferença entre Type I e Type II não é de
escopo, é de TEMPO: Type I avalia se os controles estão bem DESENHADOS
num instante — poderia, em teoria, ser satisfeito por controles recém
criados que nunca rodaram de verdade. Type II avalia se esses mesmos
controles OPERARAM efetivamente ao longo de pelo menos 6 meses — é por
isso que compradores enterprise sérios exigem Type II: ele prova
histórico de funcionamento real, não intenção documentada. Um auditor
CPA independente (não a própria empresa) emite o relatório final.</p>

<h3>14. ISO 27001: um sistema de gestão, não uma lista de caixinhas marcadas</h3>
<p>As cláusulas 4 a 10 da norma definem um Sistema de Gestão baseado no
ciclo PDCA (Plan-Do-Check-Act) — a certificação não avalia só controles
técnicos isolados, avalia se existe um PROCESSO contínuo de melhoria da
segurança da informação. O Anexo A lista 93 controles organizados em
quatro grupos (Organizacionais, Pessoas, Físicos, Tecnológicos, na
versão 2022 da norma) — mas nem todo controle se aplica a toda empresa,
e é aí que entra o SoA (Statement of Applicability): um documento formal
declarando quais controles se aplicam, quais não, e a JUSTIFICATIVA para
cada exclusão, porque "não implementamos" sem justificativa não é
aceito pelo auditor. A certificação exige auditoria interna anual mais
auditoria externa para certificar, com vigilâncias intermediárias ao
longo de um ciclo de 3 anos — não é um selo único, é uma renovação
contínua de evidência.</p>

<h3>15. Cinco anti-padrões que transformam compliance em teatro</h3>
<ul>
<li><strong>Compliance theater</strong>: políticas escritas que ninguém
lê, controles documentados que ninguém de fato aplica, evidência
fabricada às pressas para o auditor — a forma mais cara de compliance,
porque consome recursos sem reduzir risco real algum.</li>
<li><strong>Auditoria uma vez por ano em pânico</strong>: o oposto
exato do que continuous compliance (seção 7) resolve — se a empresa só
descobre o próprio estado de conformidade sob pressão de prazo, o
problema estrutural nunca foi corrigido, só escondido entre uma
auditoria e outra.</li>
<li><strong>Privacy by accident</strong>: "a gente pensa em LGPD
depois" garante retrabalho caro — redesenhar um sistema para adicionar
privacidade depois do fato é ordens de magnitude mais caro que
desenhá-lo certo desde o início (privacy by design).</li>
<li><strong>DPO sem autoridade real</strong>: um cargo criado só para
constar no organograma, sem poder de bloquear um lançamento ou exigir
correção, não cumpre a função que a lei pressupõe para o papel.</li>
<li><strong>Operador sem DPA</strong>: a empresa continua responsável
legalmente pelos dados que um fornecedor processa em seu nome — sem
contrato formal documentando essa relação, não há como demonstrar
diligência numa fiscalização.</li>
</ul>

<h3>16. Roadmap pragmático: por onde começar quando nada disso existe ainda</h3>
<ol>
<li>Identifique o framework prioritário — um cliente B2B grande exigindo
SOC 2 muda a prioridade de forma diferente de "atendemos só o mercado
brasileiro, LGPD é o mínimo inegociável".</li>
<li>Faça uma análise de lacuna (gap analysis): onde o ambiente está hoje
versus onde o framework escolhido exige que esteja.</li>
<li>Implemente os controles fundamentais primeiro — criptografia, MFA,
RBAC, log de auditoria, backup — a base que praticamente todo framework
exige, antes de qualquer controle mais específico.</li>
<li>Classifique e marque os dados com tags consistentes (seção 11), pré-requisito
para qualquer policy automatizada funcionar.</li>
<li>Adote uma ferramenta de continuous compliance adequada ao porte —
Drata/Vanta para SaaS, AWS Config para infraestrutura pura.</li>
<li>Formalize DPA com cada fornecedor que processa dado em seu nome.</li>
<li>Construa o portal de privacidade para operacionalizar os direitos do
titular sem processo manual.</li>
<li>Rode uma auditoria interna antes de contratar a externa — encontrar
os próprios gaps é mais barato que o auditor externo encontrá-los
primeiro.</li>
<li>Avance de Type I para Type II (ou equivalente) conforme o histórico
de operação acumula — Type II não é alcançável no primeiro dia, exige
tempo de operação real.</li>
</ol>"""
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
