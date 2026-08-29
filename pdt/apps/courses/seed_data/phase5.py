"""Fase 5, Escala, Resiliência e Defesa Avançada."""
from ._helpers import m, q

PHASE5 = {
    "name": "Fase 5: Escala, Resiliência e Defesa Avançada",
    "name_en": "Phase 5: Scale, Resilience and Advanced Defense",
    "description": "Domínios complexos de segurança distribuída.",
    "description_en": "Complex domains of distributed security.",
    "topics": [
        # =====================================================================
        # 5.1 Introdução ao Kubernetes
        # =====================================================================
        {
            "title": "Introdução ao Kubernetes (K8s)",
            "title_en": "Introduction to Kubernetes (K8s)",
            "summary": "Onde os microsserviços costumam morar.",
            "summary_en": "Where microservices usually live.",
            "lesson": {
                "intro": (
                    "Kubernetes é o orquestrador padrão da indústria, e com isso vem complexidade. "
                    "Antes de mergulhar em operadores, service mesh ou GitOps, é preciso dominar "
                    "os primitivos: o que é um Pod, como um Deployment difere de um StatefulSet, "
                    "por que um Service existe, como o controle declarativo funciona. Sem essa "
                    "fundação, cada feature nova vira mistério, cada erro vira exorcismo. Este "
                    "tópico te dá o modelo mental sólido para os 9 que vêm a seguir."
                ),
                "intro_en": (
                    "Kubernetes is the industry-standard orchestrator, and with that comes complexity. "
                    "Before diving into operators, service mesh, or GitOps, you need to master "
                    "the primitives: what a Pod is, how a Deployment differs from a StatefulSet, "
                    "why a Service exists, how declarative control works. Without that "
                    "foundation, every new feature becomes a mystery, every error becomes an exorcism. This "
                    "topic gives you the solid mental model for the 9 that follow."
                ),
                "body": (
                """<h3>1. O modelo mental que muda tudo: você não manda, você declara</h3>
<p>Kubernetes não é uma sequência de scripts que você executa em ordem —
é um <strong>sistema de controle baseado em estado desejado</strong>.
Você descreve o que quer ("3 réplicas de um Deployment com a imagem
nginx:1.25, expostas via Service"), envia essa descrição ao API server,
e dezenas de <em>controllers</em> trabalham em loop infinito para fazer
a realidade CONVERGIR ao que foi declarado:</p>
<div class="mermaid">
flowchart TD
    Internet["Internet"] --> Ingress["Ingress"]
    Ingress --> Service["Service"]
    Service --> Pod1["Pod 1"]
    Service --> Pod2["Pod 2"]
</div>

<pre><code># Loop conceitual de qualquer controller K8s
while True:
    desired = api.get_desired_state()  # do etcd
    actual = api.get_actual_state()    # do cluster
    diff = compare(desired, actual)
    if diff:
        apply_changes(diff)            # cria/atualiza/destrói
    sleep(short_interval)</code></pre>
<p>Isso muda a forma de OPERAR o sistema de um jeito profundo: você
nunca "manda matar um pod" diretamente — você diz "quero que este objeto
não exista" (deletando-o), e o controller correspondente RECONCILIA a
diferença. Se o objeto sumir do etcd mas o processo continuar rodando, o
kubelet o mata na próxima reconciliação. Se o objeto continuar existindo
mas o pod morrer sozinho (crash, node caindo), o controller cria outro
automaticamente. É convergência CONTÍNUA, não uma sequência de comandos
pontuais executados uma vez — a diferença central entre operar
Kubernetes e operar um script tradicional de shell.</p>

<h3>2. Arquitetura: cérebro e músculo, e por que gerenciado ganhou na maioria dos casos</h3>
<p>Um cluster tem dois grupos de nós com papéis completamente
diferentes. O <strong>control plane</strong> é o cérebro:
<code>kube-apiserver</code> é a ÚNICA porta de entrada — toda interação
com o cluster passa por ele, via REST API e streams de watch;
<code>etcd</code> é o banco de dados key-value distribuído (usando o
protocolo de consenso Raft) que guarda literalmente TODO o estado do
cluster — perdê-lo sem backup é perder o cluster inteiro;
<code>kube-scheduler</code> decide em qual node específico cada pod novo
vai rodar; <code>kube-controller-manager</code> roda os controllers
embutidos (o mesmo loop da seção 1, para Deployment, ReplicaSet, Node,
Endpoint, e outros); e <code>cloud-controller-manager</code> integra o
cluster com recursos específicos da nuvem (LoadBalancer, volumes, nodes
provisionados dinamicamente). Os <strong>workers</strong> são onde as
cargas de verdade rodam: <code>kubelet</code> é o agente presente em
cada node, recebendo a especificação de pods, conversando com o runtime
de container, e reportando status de volta; <code>kube-proxy</code>
programa as regras (iptables, ipvs, ou eBPF conforme a implementação)
que fazem os Services funcionarem de fato; e o container runtime
(containerd, CRI-O — o Docker foi descontinuado como runtime a partir do
Kubernetes 1.24) executa os containers propriamente ditos. Em clusters
gerenciados (EKS, GKE, AKS), o provedor de nuvem assume toda a
responsabilidade operacional do control plane — você só vê workers e a
API — e é por isso que a esmagadora maioria das operações em produção
usa gerenciado: operar etcd em alta disponibilidade por conta própria
não é trivial, e o ganho de fazer isso manualmente raramente compensa o
risco.</p>

<h3>3. Os primitivos que valem dominar antes de qualquer coisa mais avançada</h3>
<p>Um <strong>Pod</strong> é a menor unidade que pode ser implantada —
um ou mais containers compartilhando a mesma rede (mesmo IP, mesmas
portas) e os mesmos volumes; na prática, 99% dos pods têm um único
container, e sidecars (proxy do Istio, agente do Vault, coletor de log)
são a exceção deliberada, não a regra. Um <strong>ReplicaSet</strong>
garante que N réplicas de um pod existam — raramente criado diretamente,
quase sempre gerenciado por um Deployment. Um <strong>Deployment</strong>
gerencia ReplicaSets para fazer rolling updates de forma controlada, e é
inerentemente STATELESS: não há identidade individual entre as réplicas.
Um <strong>StatefulSet</strong> resolve o caso oposto: pods com
identidade ESTÁVEL (<code>app-0</code>, <code>app-1</code>, sempre os
mesmos nomes) e armazenamento persistente associado a cada um
especificamente — o padrão certo para bancos de dados, Kafka,
Elasticsearch. Um <strong>DaemonSet</strong> garante exatamente um pod
por node — o padrão para agentes que precisam rodar em TODO node (o
próprio CNI, coletor de log, node-exporter, Falco). <strong>Job</strong>
e <strong>CronJob</strong> cobrem trabalho em lote: Job roda até
completar uma vez, CronJob agenda Jobs com sintaxe cron. Um
<strong>Service</strong> dá um endpoint ESTÁVEL e balanceamento de
carga L4 para um conjunto de pods selecionados por label — sem ele, o IP
de cada pod muda a cada deploy e não há distribuição de tráfego nenhuma.
Um <strong>Ingress</strong> roteia HTTP/HTTPS externo por host e caminho
— mas só funciona com um ingress-controller (NGINX, Traefik, HAProxy)
efetivamente implementando o objeto declarado. <strong>ConfigMap</strong>
guarda configuração NÃO sensível; <strong>Secret</strong> guarda
configuração sensível, mas por padrão é só base64 — a aula de Hardening
detalha por que isso não é criptografia de verdade e como corrigir.
<strong>Namespace</strong> é agrupamento LÓGICO de recursos — não uma
fronteira forte de segurança por si só, apenas escopo organizacional.
<strong>PersistentVolume/PersistentVolumeClaim</strong> separam o
RECURSO de armazenamento (PV) do PEDIDO por armazenamento (PVC). E
<strong>ServiceAccount</strong> é identidade de uma CARGA de trabalho,
não de um humano — usada para autenticar programaticamente contra a
API.</p>

<h3>4. O Pod na prática: cada bloco do manifesto resolve um problema específico</h3>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:1.25@sha256:abcdef...
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    livenessProbe:
      httpGet: { path: /, port: 80 }
      periodSeconds: 10
    readinessProbe:
      httpGet: { path: /healthz, port: 80 }
      periodSeconds: 5
    securityContext:
      runAsNonRoot: true
      runAsUser: 101
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
  securityContext:
    seccompProfile:
      type: RuntimeDefault</code></pre>
<p><code>requests</code> é o valor que o SCHEDULER usa para decidir em
qual node o pod cabe — sem ele, a decisão é um "chute" sem garantia real
de recurso disponível. <code>limits</code> é o teto que o cgroup do
Linux de fato IMPÕE em runtime — sem ele, um pod com vazamento de
memória ou pico de CPU pode consumir recursos do node inteiro,
degradando todos os vizinhos que compartilham aquele node (o problema
conhecido como "noisy neighbor"). <code>livenessProbe</code> falhando
faz o kubelet REINICIAR o container — use para detectar travamento
interno (deadlock), nunca para uma dependência externa como banco de
dados, porque isso causaria uma cascata de reinícios em TODOS os pods
que dependem daquele banco assim que ele tiver um soluço momentâneo.
<code>readinessProbe</code> falhando apenas remove o pod da lista de
Endpoints do Service — sem reiniciar nada — o mecanismo certo para
"ainda estou de pé, mas não pronto para tráfego" durante aquecimento de
cache ou carga inicial. E <code>securityContext</code> (detalhado na
aula de Hardening) com <code>runAsNonRoot</code>,
<code>readOnlyRootFilesystem</code> e descarte de todas as capabilities
representa o mínimo aceitável de configuração de segurança, não um
extra opcional.</p>

<h3>5. Deployment: rolling update, e como evitar perder o cluster inteiro numa zona</h3>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: prod
spec:
  replicas: 5
  selector:
    matchLabels: { app: web }
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%       # quantos pods extras durante rollout
      maxUnavailable: 0   # zero downtime
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
      - name: web
        image: ghcr.io/me/web:v1.2.3
        # ... resources, probes, securityContext
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels: { app: web }</code></pre>
<p>A estratégia <code>RollingUpdate</code> substitui pods GRADUALMENTE
— com <code>maxUnavailable: 0</code> e <code>maxSurge: 25%</code>, novos
pods sobem ANTES dos antigos serem removidos, garantindo zero downtime
durante todo o processo. A estratégia <code>Recreate</code> (menos
comum) mata TODOS os pods antigos primeiro e só então cria os novos —
com downtime real, mas necessária quando há migração de schema de banco
incompatível entre versões, onde rodar as duas versões simultaneamente
corromperia dados. <code>topologySpreadConstraints</code> distribui as
réplicas entre zonas de disponibilidade diferentes — sem essa
configuração, o scheduler pode (por coincidência ou otimização de
recurso) colocar TODAS as réplicas na mesma zona, e perder essa zona
específica significa perder o serviço inteiro, mesmo tendo 5 réplicas
"redundantes" no papel. E usar tag mutável como <code>:latest</code> ou
<code>:main</code> na imagem é anti-padrão porque o deploy deixa de ser
REPRODUZÍVEL — o mesmo manifesto aplicado em momentos diferentes pode
puxar conteúdo de imagem diferente; prefira versionamento semântico ou,
mais forte ainda, o digest da imagem (<code>@sha256:...</code>).</p>

<h3>6. Service: por que "falar com o IP do pod" nunca funciona de verdade</h3>
<p>Pods são efetivamente descartáveis — criados e destruídos com
frequência, e o IP de cada um muda a cada recriação. A pergunta que
Service resolve é "como eu falo consistentemente com 'a aplicação web',
sem depender de um IP específico que muda a cada deploy?":</p>
<pre><code>apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector: { app: web }
  ports:
  - port: 80
    targetPort: 8080</code></pre>
<p><strong>ClusterIP</strong> (o tipo padrão) cria um IP virtual interno,
resolvido via DNS interno (<code>web.prod.svc.cluster.local</code>) —
usado para comunicação ENTRE pods dentro do cluster.
<strong>NodePort</strong> abre uma porta fixa (entre 30000 e 32767) em
TODO node do cluster — adequado para desenvolvimento e teste, raramente
para produção. <strong>LoadBalancer</strong> pede um balanceador
EXTERNO gerenciado pela nuvem (NLB da AWS, LB da GCP) — funcional, mas
caro quando multiplicado por dezenas de serviços, o que motiva combinar
com Ingress (seção 7) para expor muitos serviços através de um único
balanceador. <strong>ExternalName</strong> cria um alias DNS apontando
para um serviço FORA do cluster (por exemplo,
<code>db.prod.svc.cluster.local</code> apontando para uma instância
RDS da AWS) — útil para tratar dependências externas com a mesma
convenção de nomenclatura interna. E <strong>Headless</strong>
(<code>clusterIP: None</code>) devolve os IPs dos pods DIRETAMENTE, sem
IP virtual intermediário — necessário para StatefulSets, onde cada pod
tem identidade própria que precisa ser endereçável individualmente.</p>

<h3>7. Ingress: um único ponto de entrada para muitos serviços HTTP</h3>
<p>Um LoadBalancer dedicado por Service fica caro rapidamente conforme o
número de serviços cresce. Ingress resolve isso com um único ponto de
entrada, roteando por host e caminho para os serviços internos
corretos:</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: nginx
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service: { name: api, port: { number: 80 } }
      - path: /
        pathType: Prefix
        backend:
          service: { name: web, port: { number: 80 } }</code></pre>
<p>O objeto Ingress sozinho não faz nada — ele PRECISA de um ingress
controller instalado (NGINX, Traefik, HAProxy, ou o Ingress nativo do
GKE) que efetivamente LÊ esses objetos e configura um proxy real de
acordo. A <strong>Gateway API</strong>, mais recente, é o sucessor
designado de Ingress, com um modelo de configuração mais expressivo e
extensível — vale acompanhar sua adoção conforme amadurece.</p>

<h3>8. Três tipos de probe, e por que confundi-los causa cascata de falha</h3>
<p>Sem probes configuradas, o Kubernetes manda tráfego para um pod que
ainda está subindo (antes de estar pronto) ou nunca detecta um processo
travado internamente. Com probes MAL configuradas, um pod perfeitamente
saudável entra em loop de reinício por motivo errado. A distinção entre
os três tipos é essencial: <code>livenessProbe</code> pergunta "estou
vivo?" — falhar reinicia o CONTAINER; nunca deve depender de uma
dependência EXTERNA (banco de dados), porque isso causaria falha em
cascata: se o banco tiver um soluço momentâneo, TODOS os pods que o
consultam na liveness probe reiniciariam simultaneamente, piorando uma
situação que já era ruim. <code>readinessProbe</code> pergunta "posso
receber tráfego agora?" — falhar remove o pod do Service, MAS não o
reinicia; é o lugar certo para checar aquecimento de cache ou
dependência que ainda não terminou de conectar.
<code>startupProbe</code> pergunta "já terminei de iniciar?" — roda
PRIMEIRO, e enquanto não passar, liveness e readiness ficam suspensas;
essencial para aplicações com boot lento (Java, .NET), onde sem essa
proteção a liveness probe reiniciaria o container repetidamente antes
mesmo dele terminar de inicializar pela primeira vez:</p>
<pre><code># Bom
livenessProbe:
  exec: { command: ["/bin/sh", "-c", "pgrep -f myapp || exit 1"] }
  periodSeconds: 30
  failureThreshold: 3
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  periodSeconds: 5
  failureThreshold: 1
startupProbe:
  httpGet: { path: /healthz, port: 8080 }
  periodSeconds: 10
  failureThreshold: 30  # 5 min para subir</code></pre>

<h3>9. ConfigMap e Secret: mesma mecânica, garantias bem diferentes</h3>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata: { name: app-config }
data:
  log_level: info
  api_url: https://api.example.com
---
apiVersion: v1
kind: Secret
metadata: { name: app-secret }
type: Opaque
data:
  db_password: cGFzczEyMw==  # base64</code></pre>
<p>Os dois podem ser injetados em pods das mesmas duas formas — como
variável de ambiente ou montados como arquivo:</p>
<pre><code>spec:
  containers:
  - name: app
    envFrom:
    - configMapRef: { name: app-config }
    - secretRef: { name: app-secret }
    # ou monte como arquivo
    volumeMounts:
    - name: secret-vol
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-vol
    secret: { secretName: app-secret }</code></pre>
<p>A diferença crítica entre os dois não está na mecânica de uso — está
na (falsa) sensação de segurança: Secret é apenas CODIFICADO em base64,
não criptografado, uma codificação reversível sem chave nenhuma. Em
produção, o padrão recomendado é usar um External Secrets Operator
(puxando de Vault ou AWS Secrets Manager em tempo real) ou SealedSecrets
da Bitnami (para permitir versionar segredos criptografados em Git, no
fluxo GitOps da seção 11) — e em qualquer caso, ter encryption-at-rest
habilitado no etcd (detalhado na aula de Hardening) como camada
adicional.</p>

<h3>10. Helm: parametrizar o mesmo manifesto para ambientes diferentes</h3>
<p>Manter o mesmo YAML repetido manualmente em quatro ambientes
(dev/qa/staging/prod), com pequenas diferenças espalhadas entre cópias,
vira fonte constante de divergência e erro. Helm empacota manifestos em
<em>charts</em>, usando templates (na linguagem de template do Go) mais
um arquivo de <em>values</em> específico por ambiente:</p>
<pre><code>mychart/
├── Chart.yaml
├── values.yaml          # defaults
├── values-prod.yaml     # overrides
└── templates/
    ├── deployment.yaml
    └── service.yaml

$ helm install myapp ./mychart -f values-prod.yaml --namespace prod
$ helm upgrade myapp ./mychart -f values-prod.yaml --namespace prod
$ helm rollback myapp 1 --namespace prod</code></pre>
<p>Charts podem ser publicados num registry OCI (ECR, GAR, GHCR) e
versionados exatamente como uma imagem de container — o mesmo fluxo de
tag e pull, aplicado a pacotes de manifesto. Kustomize (overlays de
YAML puro, sem motor de template) e operadores (controllers customizados
que entendem CRDs específicos) são alternativas para casos onde
templating completo é excessivo ou insuficiente, respectivamente.</p>

<h3>11. GitOps: o repositório Git como única fonte da verdade do cluster</h3>
<p>Rodar <code>kubectl apply</code> manualmente contra produção, direto
do laptop de alguém, é cada vez mais raro em operações maduras — não por
tradição, mas porque perde rastreabilidade e permissão granular. GitOps
inverte o fluxo: o repositório Git se torna a fonte de verdade
declarada, e uma ferramenta dentro do cluster mantém a realidade
sincronizada com ele.</p>
<ol>
<li>Um engenheiro abre um PR alterando o manifesto no repositório.</li>
<li>O PR passa por revisão normal e é mergeado.</li>
<li>Argo CD (rodando dentro do próprio cluster) detecta o novo commit,
compara com o estado atual do cluster, e aplica a diferença.</li>
<li>Se alguém alterar algo manualmente no cluster (drift), o Argo detecta
essa divergência e reverte automaticamente ou alerta, conforme a
configuração.</li>
</ol>
<p>Os benefícios concretos: trilha de auditoria vem de graça do próprio
histórico do Git; rollback é literalmente um <code>git revert</code>,
sem comando especial de infraestrutura; e engenheiros individuais não
precisam mais de acesso direto via <code>kubectl</code> a produção — o
Argo CD é quem detém essa permissão, reduzindo a superfície de acesso
humano direto ao cluster real.</p>

<h3>12. Distribuições: do laptop ao cluster gerenciado em produção</h3>
<p><strong>kind</strong> e <strong>minikube</strong> rodam Kubernetes
localmente para desenvolvimento e teste — sem custo de nuvem, sem
disponibilidade real, exatamente o propósito. <strong>k3s</strong> e
<strong>k0s</strong> são distribuições leves voltadas a edge, IoT ou
ambientes de CI, onde o overhead de um cluster completo não se justifica.
<strong>kubeadm</strong> monta um cluster "vanilla" manualmente — ótimo
para aprender o que cada componente faz de verdade, raro em produção
justamente pelo esforço operacional contínuo que exige.
<strong>OpenShift, Rancher</strong> e <strong>Tanzu</strong> são
distribuições comerciais com funcionalidades extras sobre o Kubernetes
padrão. E <strong>EKS, GKE, AKS</strong> são as opções gerenciadas, onde
o provedor de nuvem opera o control plane inteiro. Para a esmagadora
maioria dos casos, gerenciado é a escolha certa — self-host só se
justifica por exigência específica de compliance, ambiente de edge, ou
hardware bare-metal com necessidade particular que a nuvem gerenciada
não atende.</p>

<h3>13. Comandos `kubectl` que resolvem 90% do dia a dia</h3>
<pre><code># Visualizar
kubectl get pods -n prod -o wide
kubectl describe pod web-abc -n prod
kubectl logs -f web-abc -n prod
kubectl logs --previous web-abc -n prod  # após restart
kubectl top pod -n prod                  # CPU/RAM

# Aplicar/remover
kubectl apply -f manifests/
kubectl delete -f manifests/web.yaml
kubectl scale deploy web --replicas=10 -n prod

# Debug
kubectl exec -it web-abc -n prod -- /bin/sh
kubectl port-forward svc/web 8080:80 -n prod
kubectl run debug --rm -it --image=busybox -- sh
kubectl debug -it web-abc --image=busybox -n prod  # ephemeral container

# Diff e dry-run
kubectl diff -f manifest.yaml
kubectl apply -f manifest.yaml --dry-run=server

# Eventos (chave em troubleshooting)
kubectl get events -n prod --sort-by=.lastTimestamp</code></pre>
<p>Um detalhe que vale destacar entre esses comandos: <code>kubectl logs
--previous</code> recupera os logs do container ANTERIOR a um reinício
— sem essa flag específica, você vê os logs do processo atual, que pode
não ter nenhuma pista sobre o que causou o crash anterior.
<code>kubectl get events</code> ordenado por timestamp é frequentemente
a primeira parada num troubleshooting real, porque revela ações do
próprio Kubernetes (scheduling falhou, imagem não foi encontrada, probe
falhando) que não aparecem nem nos logs da aplicação nem no
<code>describe</code> de um objeto isolado.</p>

<h3>14. Sete anti-padrões que aparecem em praticamente todo cluster iniciante</h3>
<ul>
<li><strong>Pod sem requests/limits</strong>: o scheduler decide sem
informação real, e um "vizinho barulhento" consegue afetar outros
workloads no mesmo node.</li>
<li><strong>livenessProbe dependente de banco externo</strong>: causa
falha em cascata exatamente no momento em que o banco já está com
problema — o pior momento possível para reiniciar tudo simultaneamente.</li>
<li><strong>Imagem com tag `:latest`</strong>: deploy deixa de ser
reproduzível, o mesmo manifesto aplicado hoje e amanhã pode puxar
conteúdo diferente sem nenhuma mudança visível no YAML.</li>
<li><strong>Tudo no namespace `default`</strong>: aplicar NetworkPolicy
ou RBAC granular vira praticamente impossível sem segmentação lógica
mínima por namespace.</li>
<li><strong>Log gravado em arquivo dentro do pod</strong>: viola o
princípio dos 12 fatores de aplicação cloud-native; use stdout, e deixe
a coleta de log ser responsabilidade da infraestrutura, não da
aplicação.</li>
<li><strong>hostPath como "persistência"</strong>: escapa do isolamento
de container ao amarrar o pod a um caminho específico do NODE
físico — use PersistentVolume, que é portável entre nodes.</li>
<li><strong>Uma única réplica em produção</strong>: qualquer manutenção
de node (planejada ou não) derruba a aplicação inteira, porque não há
segunda réplica para absorver o tráfego durante o rolling update.</li>
</ul>

<h3>15. Quando Kubernetes é a ferramenta ERRADA para o problema</h3>
<p>Kubernetes é poderoso, mas carrega custo operacional real — para
aplicações simples (um a três serviços, tráfego baixo), Docker Compose,
ECS, Cloud Run ou Fly.io entregam o mesmo resultado prático com uma
fração da complexidade operacional. Kubernetes se justifica quando existem
dezenas ou mais de microsserviços coordenados, necessidade real de
autoscaling complexo, exigência de compliance que demanda observabilidade
e política avançadas (as próximas nove aulas desta fase), ou um time
grande o suficiente trabalhando em paralelo para que a coordenação
declarativa valha o overhead de aprendizado. Adotar Kubernetes só porque
"virou o padrão da indústria", sem que o problema real da organização o
exija, troca simplicidade real por complexidade que não paga o próprio
custo.</p>"""
                ),
                "body_en": (
                """<h3>1. The mental model that changes everything: you don't command, you declare</h3>
<p>Kubernetes is not a sequence of scripts you run in order —
it's a <strong>control system based on desired state</strong>.
You describe what you want ("3 replicas of a Deployment with the
nginx:1.25 image, exposed via a Service"), send that description to the API
server, and dozens of <em>controllers</em> work in an infinite loop to make
reality CONVERGE to what was declared:</p>
<div class="mermaid">
flowchart TD
    Internet["Internet"] --> Ingress["Ingress"]
    Ingress --> Service["Service"]
    Service --> Pod1["Pod 1"]
    Service --> Pod2["Pod 2"]
</div>
<pre><code># Loop conceitual de qualquer controller K8s
while True:
    desired = api.get_desired_state()  # do etcd
    actual = api.get_actual_state()    # do cluster
    diff = compare(desired, actual)
    if diff:
        apply_changes(diff)            # cria/atualiza/destrói
    sleep(short_interval)</code></pre>
<p>This changes how you OPERATE the system in a profound way: you
never "command a pod to die" directly — you say "I want this object
not to exist" (by deleting it), and the corresponding controller RECONCILES the
difference. If the object disappears from etcd but the process keeps running, the
kubelet kills it on the next reconciliation. If the object still exists
but the pod dies on its own (crash, node going down), the controller creates another one
automatically. It's CONTINUOUS convergence, not a sequence of one-off
commands executed once — the central difference between operating
Kubernetes and operating a traditional shell script.</p>

<h3>2. Architecture: brain and muscle, and why managed won in most cases</h3>
<p>A cluster has two groups of nodes with completely
different roles. The <strong>control plane</strong> is the brain:
<code>kube-apiserver</code> is the ONLY entry point — every interaction
with the cluster goes through it, via REST API and watch streams;
<code>etcd</code> is the distributed key-value database (using the
Raft consensus protocol) that holds literally ALL of the cluster's
state — losing it without a backup means losing the entire cluster;
<code>kube-scheduler</code> decides which specific node each new pod
will run on; <code>kube-controller-manager</code> runs the built-in
controllers (the same loop from section 1, for Deployment, ReplicaSet, Node,
Endpoint, and others); and <code>cloud-controller-manager</code> integrates the
cluster with cloud-specific resources (LoadBalancer, volumes, dynamically
provisioned nodes). The <strong>workers</strong> are where the actual
workloads run: <code>kubelet</code> is the agent present on
each node, receiving pod specs, talking to the container
runtime, and reporting status back; <code>kube-proxy</code>
programs the rules (iptables, ipvs, or eBPF depending on the
implementation) that actually make Services work; and the container runtime
(containerd, CRI-O — Docker was discontinued as a runtime starting with
Kubernetes 1.24) runs the containers themselves. In managed
clusters (EKS, GKE, AKS), the cloud provider takes on the entire
operational responsibility for the control plane — you only see workers and the
API — and that's why the overwhelming majority of production operations
use managed clusters: running etcd in high availability on your own
is nontrivial, and the gain from doing it manually rarely offsets the
risk.</p>

<h3>3. The primitives worth mastering before anything more advanced</h3>
<p>A <strong>Pod</strong> is the smallest deployable unit —
one or more containers sharing the same network (same IP, same
ports) and the same volumes; in practice, 99% of pods have a single
container, and sidecars (Istio's proxy, Vault's agent, a log
collector) are the deliberate exception, not the rule. A <strong>ReplicaSet</strong>
guarantees that N replicas of a pod exist — rarely created directly,
almost always managed by a Deployment. A <strong>Deployment</strong>
manages ReplicaSets to perform rolling updates in a controlled way, and is
inherently STATELESS: there's no individual identity between replicas.
A <strong>StatefulSet</strong> solves the opposite case: pods with
STABLE identity (<code>app-0</code>, <code>app-1</code>, always the
same names) and persistent storage tied to each one
specifically — the right pattern for databases, Kafka,
Elasticsearch. A <strong>DaemonSet</strong> guarantees exactly one pod
per node — the pattern for agents that need to run on EVERY node (the
CNI itself, a log collector, node-exporter, Falco). <strong>Job</strong>
and <strong>CronJob</strong> cover batch work: Job runs until it
completes once, CronJob schedules Jobs with cron syntax. A
<strong>Service</strong> gives a STABLE endpoint and L4 load
balancing for a set of pods selected by label — without it, each pod's
IP changes on every deploy and there's no traffic distribution
whatsoever. An <strong>Ingress</strong> routes external HTTP/HTTPS by host and path
— but only works with an ingress-controller (NGINX, Traefik, HAProxy)
actually implementing the declared object. <strong>ConfigMap</strong>
holds NON-sensitive configuration; <strong>Secret</strong> holds
sensitive configuration, but by default it's just base64 — the Hardening
lesson details why that isn't real encryption and how to fix it.
<strong>Namespace</strong> is LOGICAL grouping of resources — not a
strong security boundary on its own, just organizational scope.
<strong>PersistentVolume/PersistentVolumeClaim</strong> separate the storage
RESOURCE (PV) from the REQUEST for storage (PVC). And
<strong>ServiceAccount</strong> is the identity of a WORKLOAD,
not a human — used to authenticate programmatically against the
API.</p>

<h3>4. The Pod in practice: each block in the manifest solves a specific problem</h3>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:1.25@sha256:abcdef...
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    livenessProbe:
      httpGet: { path: /, port: 80 }
      periodSeconds: 10
    readinessProbe:
      httpGet: { path: /healthz, port: 80 }
      periodSeconds: 5
    securityContext:
      runAsNonRoot: true
      runAsUser: 101
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
  securityContext:
    seccompProfile:
      type: RuntimeDefault</code></pre>
<p><code>requests</code> is the value the SCHEDULER uses to decide on
which node the pod fits — without it, the decision is a "guess" with no real
guarantee of available resources. <code>limits</code> is the ceiling the Linux
cgroup actually ENFORCES at runtime — without it, a pod with a memory
leak or CPU spike can consume the resources of the entire node,
degrading every neighbor sharing that node (the problem
known as the "noisy neighbor"). A failing <code>livenessProbe</code>
makes the kubelet RESTART the container — use it to detect internal
lockup (deadlock), never for an external dependency like a database,
because that would cause a cascade of restarts across EVERY pod
that depends on that database as soon as it has a momentary hiccup.
A failing <code>readinessProbe</code> only removes the pod from the Service's
Endpoints list — without restarting anything — the right mechanism
for "I'm still standing, but not ready for traffic" during cache
warm-up or initial load. And <code>securityContext</code> (detailed in
the Hardening lesson) with <code>runAsNonRoot</code>,
<code>readOnlyRootFilesystem</code>, and dropping all capabilities
represents the minimum acceptable security configuration, not an
optional extra.</p>

<h3>5. Deployment: rolling update, and how to avoid losing the entire cluster in one zone</h3>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: prod
spec:
  replicas: 5
  selector:
    matchLabels: { app: web }
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%       # quantos pods extras durante rollout
      maxUnavailable: 0   # zero downtime
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
      - name: web
        image: ghcr.io/me/web:v1.2.3
        # ... resources, probes, securityContext
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels: { app: web }</code></pre>
<p>The <code>RollingUpdate</code> strategy replaces pods GRADUALLY
— with <code>maxUnavailable: 0</code> and <code>maxSurge: 25%</code>, new
pods come up BEFORE the old ones are removed, guaranteeing zero downtime
throughout the whole process. The <code>Recreate</code> strategy (less
common) kills ALL old pods first and only then creates the new ones —
with real downtime, but necessary when there's an incompatible database
schema migration between versions, where running both versions simultaneously
would corrupt data. <code>topologySpreadConstraints</code> distributes
replicas across different availability zones — without this
configuration, the scheduler might (by coincidence or resource
optimization) place ALL replicas in the same zone, and losing that
specific zone means losing the entire service, even with 5 "redundant"
replicas on paper. And using a mutable tag like <code>:latest</code> or
<code>:main</code> on the image is an anti-pattern because the deploy stops being
REPRODUCIBLE — the same manifest applied at different times might
pull different image content; prefer semantic versioning or,
stronger still, the image digest (<code>@sha256:...</code>).</p>

<h3>6. Service: why "talking to the pod's IP" never really works</h3>
<p>Pods are effectively disposable — created and destroyed
frequently, and each one's IP changes on every recreation. The question that
Service solves is "how do I consistently talk to 'the web application',
without depending on a specific IP that changes on every deploy?":</p>
<pre><code>apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector: { app: web }
  ports:
  - port: 80
    targetPort: 8080</code></pre>
<p><strong>ClusterIP</strong> (the default type) creates an internal virtual IP,
resolved via internal DNS (<code>web.prod.svc.cluster.local</code>) —
used for communication BETWEEN pods within the cluster.
<strong>NodePort</strong> opens a fixed port (between 30000 and 32767) on
EVERY node in the cluster — suitable for development and testing, rarely
for production. <strong>LoadBalancer</strong> requests an
EXTERNAL load balancer managed by the cloud (AWS's NLB, GCP's LB) — functional, but
expensive when multiplied across dozens of services, which motivates combining
it with Ingress (section 7) to expose many services through a single
load balancer. <strong>ExternalName</strong> creates a DNS alias pointing
to a service OUTSIDE the cluster (for example,
<code>db.prod.svc.cluster.local</code> pointing to an AWS
RDS instance) — useful for treating external dependencies with the same
internal naming convention. And <strong>Headless</strong>
(<code>clusterIP: None</code>) returns the pods' IPs DIRECTLY, without
an intermediate virtual IP — necessary for StatefulSets, where each pod
has its own identity that needs to be individually addressable.</p>

<h3>7. Ingress: a single entry point for many HTTP services</h3>
<p>A dedicated LoadBalancer per Service gets expensive quickly as the
number of services grows. Ingress solves this with a single entry
point, routing by host and path to the correct internal
services:</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: nginx
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service: { name: api, port: { number: 80 } }
      - path: /
        pathType: Prefix
        backend:
          service: { name: web, port: { number: 80 } }</code></pre>
<p>The Ingress object alone does nothing — it NEEDS an ingress
controller installed (NGINX, Traefik, HAProxy, or GKE's native Ingress)
that actually READS these objects and configures a real proxy
accordingly. The <strong>Gateway API</strong>, newer, is the designated
successor to Ingress, with a more expressive and extensible
configuration model — worth watching as its adoption matures.</p>

<h3>8. Three types of probe, and why confusing them causes a failure cascade</h3>
<p>Without probes configured, Kubernetes sends traffic to a pod that's
still starting up (before it's ready) or never detects a process stuck
internally. With BADLY configured probes, a perfectly
healthy pod enters a restart loop for the wrong reason. The distinction between
the three types is essential: <code>livenessProbe</code> asks "am I
alive?" — failing RESTARTS the CONTAINER; it should never depend on an
EXTERNAL dependency (a database), because that would cause a cascading
failure: if the database has a momentary hiccup, EVERY pod that
queries it in the liveness probe would restart simultaneously, worsening a
situation that was already bad. <code>readinessProbe</code> asks "can I
receive traffic now?" — failing removes the pod from the Service, BUT
doesn't restart it; it's the right place to check cache
warm-up or a dependency that hasn't finished connecting yet.
<code>startupProbe</code> asks "have I finished starting?" — it runs
FIRST, and until it passes, liveness and readiness are suspended;
essential for applications with slow boot (Java, .NET), where without this
protection the liveness probe would restart the container repeatedly before
it even finishes initializing for the first time:</p>
<pre><code># Bom
livenessProbe:
  exec: { command: ["/bin/sh", "-c", "pgrep -f myapp || exit 1"] }
  periodSeconds: 30
  failureThreshold: 3
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  periodSeconds: 5
  failureThreshold: 1
startupProbe:
  httpGet: { path: /healthz, port: 8080 }
  periodSeconds: 10
  failureThreshold: 30  # 5 min para subir</code></pre>

<h3>9. ConfigMap and Secret: same mechanics, very different guarantees</h3>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata: { name: app-config }
data:
  log_level: info
  api_url: https://api.example.com
---
apiVersion: v1
kind: Secret
metadata: { name: app-secret }
type: Opaque
data:
  db_password: cGFzczEyMw==  # base64</code></pre>
<p>Both can be injected into pods the same two ways — as an
environment variable or mounted as a file:</p>
<pre><code>spec:
  containers:
  - name: app
    envFrom:
    - configMapRef: { name: app-config }
    - secretRef: { name: app-secret }
    # ou monte como arquivo
    volumeMounts:
    - name: secret-vol
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-vol
    secret: { secretName: app-secret }</code></pre>
<p>The critical difference between the two isn't in the usage mechanics — it's
in the (false) sense of security: Secret is only base64-ENCODED,
not encrypted, a reversible encoding with no key at all. In
production, the recommended standard is to use an External Secrets Operator
(pulling from Vault or AWS Secrets Manager in real time) or Bitnami's
SealedSecrets (to allow versioning encrypted secrets in Git, in the
GitOps flow from section 11) — and in any case, having
encryption-at-rest enabled on etcd (detailed in the Hardening
lesson) as an additional layer.</p>

<h3>10. Helm: parameterizing the same manifest for different environments</h3>
<p>Keeping the same YAML manually duplicated across four environments
(dev/qa/staging/prod), with small differences scattered across copies,
becomes a constant source of drift and error. Helm packages manifests into
<em>charts</em>, using templates (in Go's templating language) plus
a per-environment <em>values</em> file:</p>
<pre><code>mychart/
├── Chart.yaml
├── values.yaml          # defaults
├── values-prod.yaml     # overrides
└── templates/
    ├── deployment.yaml
    └── service.yaml

$ helm install myapp ./mychart -f values-prod.yaml --namespace prod
$ helm upgrade myapp ./mychart -f values-prod.yaml --namespace prod
$ helm rollback myapp 1 --namespace prod</code></pre>
<p>Charts can be published to an OCI registry (ECR, GAR, GHCR) and
versioned exactly like a container image — the same tag-and-pull
flow, applied to manifest packages. Kustomize (plain YAML overlays,
no templating engine) and operators (custom controllers
that understand specific CRDs) are alternatives for cases where
full templating is excessive or insufficient, respectively.</p>

<h3>11. GitOps: the Git repository as the single source of truth for the cluster</h3>
<p>Running <code>kubectl apply</code> manually against production, straight
from someone's laptop, is increasingly rare in mature operations — not out of
tradition, but because it loses traceability and granular permission. GitOps
inverts the flow: the Git repository becomes the declared
source of truth, and a tool inside the cluster keeps
reality synchronized with it.</p>
<ol>
<li>An engineer opens a PR changing the manifest in the repository.</li>
<li>The PR goes through normal review and is merged.</li>
<li>Argo CD (running inside the cluster itself) detects the new commit,
compares it with the cluster's current state, and applies the difference.</li>
<li>If someone manually changes something in the cluster (drift), Argo detects
that divergence and either reverts it automatically or alerts, depending on the
configuration.</li>
</ol>
<p>The concrete benefits: an audit trail comes for free from the Git
history itself; rollback is literally a <code>git revert</code>,
with no special infrastructure command; and individual engineers no
longer need direct <code>kubectl</code> access to production — the
Argo CD holds that permission instead, reducing the surface of direct
human access to the real cluster.</p>

<h3>12. Distributions: from laptop to managed cluster in production</h3>
<p><strong>kind</strong> and <strong>minikube</strong> run Kubernetes
locally for development and testing — no cloud cost, no real
availability, exactly the point. <strong>k3s</strong> and
<strong>k0s</strong> are lightweight distributions aimed at edge, IoT, or
CI environments, where the overhead of a full cluster isn't justified.
<strong>kubeadm</strong> assembles a "vanilla" cluster manually — great
for learning what each component actually does, rare in production
precisely because of the ongoing operational effort it requires.
<strong>OpenShift, Rancher</strong>, and <strong>Tanzu</strong> are
commercial distributions with extra features on top of standard Kubernetes.
And <strong>EKS, GKE, AKS</strong> are the managed options, where
the cloud provider operates the entire control plane. For the
overwhelming majority of cases, managed is the right choice — self-hosting only
makes sense for a specific compliance requirement, an edge
environment, or bare-metal hardware with a particular need that
managed cloud doesn't meet.</p>

<h3>13. `kubectl` commands that solve 90% of day-to-day work</h3>
<pre><code># Visualizar
kubectl get pods -n prod -o wide
kubectl describe pod web-abc -n prod
kubectl logs -f web-abc -n prod
kubectl logs --previous web-abc -n prod  # após restart
kubectl top pod -n prod                  # CPU/RAM

# Aplicar/remover
kubectl apply -f manifests/
kubectl delete -f manifests/web.yaml
kubectl scale deploy web --replicas=10 -n prod

# Debug
kubectl exec -it web-abc -n prod -- /bin/sh
kubectl port-forward svc/web 8080:80 -n prod
kubectl run debug --rm -it --image=busybox -- sh
kubectl debug -it web-abc --image=busybox -n prod  # ephemeral container

# Diff e dry-run
kubectl diff -f manifest.yaml
kubectl apply -f manifest.yaml --dry-run=server

# Eventos (chave em troubleshooting)
kubectl get events -n prod --sort-by=.lastTimestamp</code></pre>
<p>One detail worth highlighting among these commands: <code>kubectl logs
--previous</code> recovers the logs of the container BEFORE a restart
— without this specific flag, you see the current process's logs, which might
have no clue about what caused the previous crash.
<code>kubectl get events</code> sorted by timestamp is often
the first stop in real troubleshooting, because it reveals actions taken by
Kubernetes itself (scheduling failed, image not found, probe
failing) that don't show up in the application logs or in an isolated
object's <code>describe</code>.</p>

<h3>14. Seven anti-patterns that show up in practically every beginner cluster</h3>
<ul>
<li><strong>Pod with no requests/limits</strong>: the scheduler decides without
real information, and a "noisy neighbor" can affect other
workloads on the same node.</li>
<li><strong>livenessProbe dependent on an external database</strong>: causes
a cascading failure exactly at the moment the database is already having
problems — the worst possible time to restart everything simultaneously.</li>
<li><strong>Image with a `:latest` tag</strong>: the deploy stops being
reproducible, the same manifest applied today and tomorrow might pull
different content with no visible change in the YAML.</li>
<li><strong>Everything in the `default` namespace</strong>: applying granular
NetworkPolicy or RBAC becomes practically impossible without minimal
logical segmentation by namespace.</li>
<li><strong>Logs written to a file inside the pod</strong>: violates the
12-factor principle for cloud-native applications; use stdout, and let
log collection be the infrastructure's responsibility, not the
application's.</li>
<li><strong>hostPath as "persistence"</strong>: escapes container
isolation by tying the pod to a specific path on the physical
NODE — use PersistentVolume, which is portable between nodes.</li>
<li><strong>A single replica in production</strong>: any node
maintenance (planned or not) takes down the entire application, because there's no
second replica to absorb traffic during the rolling update.</li>
</ul>

<h3>15. When Kubernetes is the WRONG tool for the problem</h3>
<p>Kubernetes is powerful, but carries real operational cost — for
simple applications (one to three services, low traffic), Docker Compose,
ECS, Cloud Run, or Fly.io deliver the same practical result with a
fraction of the operational complexity. Kubernetes is justified when there are
dozens or more coordinated microservices, a real need for
complex autoscaling, a compliance requirement demanding advanced
observability and policy (the next nine lessons in this phase), or a
team large enough working in parallel that declarative coordination
is worth the learning overhead. Adopting Kubernetes just because
"it became the industry standard," without the organization's actual problem
requiring it, trades real simplicity for complexity that doesn't pay for its
own cost.</p>"""
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
                "practical_en": (
                    "Spin up a local <code>kind create cluster</code>. Create an NGINX Deployment "
                    "with 3 replicas via <code>kubectl create deploy nginx --image=nginx:1.25 "
                    "--replicas=3</code>. Expose it via <code>kubectl expose deploy nginx --port=80 "
                    "--type=ClusterIP</code>. Use <code>kubectl port-forward svc/nginx 8080:80</code> "
                    "and open <code>http://localhost:8080</code>. Then write a "
                    "Deployment+Service+ConfigMap manifest in YAML, apply it with <code>kubectl apply</code>, "
                    "and afterwards remove it with <code>kubectl delete -f</code>. Finally, install the NGINX "
                    "Ingress Controller via Helm and create an Ingress routing <code>app.local</code> "
                    "to the Service."
                ),
            },
            "materials": [
                m("Kubernetes Docs", "https://kubernetes.io/docs/home/", "docs", "", title_en="Kubernetes Docs", description_en=""),
                m("Kubernetes the Hard Way", "https://github.com/kelseyhightower/kubernetes-the-hard-way", "course", "", title_en="Kubernetes the Hard Way", description_en=""),
                m("kind (local k8s)", "https://kind.sigs.k8s.io/", "tool", "", title_en="kind (local k8s)", description_en=""),
                m("Helm", "https://helm.sh/docs/", "docs", "", title_en="Helm", description_en=""),
                m("ArgoCD", "https://argo-cd.readthedocs.io/", "tool", "", title_en="ArgoCD", description_en=""),
                m("k8s.io: Tutorials", "https://kubernetes.io/docs/tutorials/", "course", "", title_en="k8s.io: Tutorials", description_en=""),
                m("Kubernetes Patterns (livro)", "https://k8spatterns.io/", "book", "", title_en="Kubernetes Patterns (book)", description_en=""),
                m("Kubernetes Failure Stories", "https://k8s.af/", "article", "Aprender pelos erros dos outros.", title_en="Kubernetes Failure Stories", description_en="Learn from other people's mistakes."),
            ],
            "questions": [
                q("Pod é:",
                  "Menor unidade deployable, com 1+ containers compartilhando rede e volumes.",
                  ["Um tipo específico de recurso Service dentro do cluster, atalho que ignora exatamente o cenário que mais importa evitar.", "O cluster inteiro, com vários nodes e workloads, comportamento que só vira prioridade depois que já causou prejuízo.", "Só a versão instalada do binário kubectl, resultado típico de copiar configuração de outro projeto sem adaptar."],
                  "Pod tem 1 IP, namespace de rede comum. Containers laterais (sidecar) compartilham.",
                  statement_en="A Pod is:",
                  correct_en="The smallest deployable unit, with 1+ containers sharing network and volumes.",
                  wrong_en=["A specific type of Service resource inside the cluster, a shortcut that skips exactly the scenario most worth avoiding.", "The entire cluster, with several nodes and workloads, behavior that only becomes a priority after it has already caused damage.", "Just the installed version of the kubectl binary, a typical result of copying configuration from another project without adapting it."],
                  explanation_en="A Pod has 1 IP, a shared network namespace. Sidecar containers share it."),
                q("Deployment garante:",
                  "Estado desejado de réplicas e rolling update.",
                  ["Substitui a necessidade de configurar um Service.", "Funciona só dentro do namespace default do cluster.", "Mantém geralmente exatamente um único pod rodando."],
                  "Cria/gerencia ReplicaSets. Update gradual com max-surge/max-unavailable.",
                  statement_en="A Deployment guarantees:",
                  correct_en="Desired replica state and rolling update.",
                  wrong_en=["Replaces the need to configure a Service.", "Only works inside the cluster's default namespace.", "Usually keeps exactly a single pod running."],
                  explanation_en="Creates/manages ReplicaSets. Gradual update with max-surge/max-unavailable."),
                q("Service do tipo ClusterIP:",
                  "Expõe internamente ao cluster.",
                  ["Funciona só sobre endereçamento IPv6 configurado.", "Expõe o serviço diretamente para a internet pública.", "Funciona só para tráfego usando o protocolo TCP."],
                  "Para externo: NodePort, LoadBalancer ou Ingress (preferido para HTTP).",
                  statement_en="A ClusterIP-type Service:",
                  correct_en="Exposes the service internally within the cluster.",
                  wrong_en=["Only works over configured IPv6 addressing.", "Exposes the service directly to the public internet.", "Only works for traffic using the TCP protocol."],
                  explanation_en="For external access: NodePort, LoadBalancer, or Ingress (preferred for HTTP)."),
                q("Ingress serve para:",
                  "Roteamento HTTP/S externo.",
                  ["Um tipo de roteamento voltado a armazenamento em disco.", "Só cuida da resolução de nomes DNS do domínio.", "Substitui por completo a necessidade de um Service."],
                  "Precisa de ingress-controller (NGINX, Traefik) implementando o objeto Ingress.",
                  statement_en="Ingress is used for:",
                  correct_en="External HTTP/S routing.",
                  wrong_en=["A type of routing aimed at disk storage.", "It only handles DNS name resolution for the domain.", "Completely replaces the need for a Service."],
                  explanation_en="Needs an ingress-controller (NGINX, Traefik) implementing the Ingress object."),
                q("ConfigMap e Secret:",
                  "Injetam configuração e segredos em pods.",
                  ["São exatamente o mesmo tipo de recurso do cluster.", "Funcionam como volume de armazenamento persistente.", "Guardam métricas coletadas do cluster em tempo real."],
                  "Secret é base64, não cripto. Habilite encryption-at-rest no etcd e use externos.",
                  statement_en="ConfigMap and Secret:",
                  correct_en="Inject configuration and secrets into pods.",
                  wrong_en=["Are exactly the same type of cluster resource.", "Work as a persistent storage volume.", "Store metrics collected from the cluster in real time."],
                  explanation_en="Secret is base64, not encryption. Enable encryption-at-rest on etcd and use external stores."),
                q("kubectl apply:",
                  "Aplica manifests declarativos.",
                  ["Cria um novo chart Helm a partir do manifest.", "Apaga o cluster inteiro junto com vários nodes.", "Substitui a necessidade de rodar o kubelet no node."],
                  "Idempotente. Compara desejado vs atual e ajusta. Use server-side apply em casos avançados.",
                  statement_en="kubectl apply:",
                  correct_en="Applies declarative manifests.",
                  wrong_en=["Creates a new Helm chart from the manifest.", "Deletes the entire cluster along with several nodes.", "Replaces the need to run the kubelet on the node."],
                  explanation_en="Idempotent. Compares desired vs. actual and adjusts. Use server-side apply for advanced cases."),
                q("Helm chart é:",
                  "Pacote de manifests com templates e values.",
                  ["Uma alternativa completa que substitui o próprio kubectl.", "Um arquivo YAML estático sem algum tipo de template.", "Um banco de dados usado para guardar estado do cluster."],
                  "Permite parametrizar releases por ambiente. Subindo charts em registry OCI versiona como imagem.",
                  statement_en="A Helm chart is:",
                  correct_en="A package of manifests with templates and values.",
                  wrong_en=["A complete alternative that replaces kubectl itself.", "A static YAML file without any kind of template.", "A database used to store cluster state."],
                  explanation_en="Lets you parameterize releases per environment. Pushing charts to an OCI registry versions them like an image."),
                q("Namespace serve para:",
                  "Isolar recursos logicamente no cluster.",
                  ["Substitui a necessidade de configurar uma VPC na nuvem.", "Serve só para organizar regras de RBAC no cluster.", "Substitui a necessidade de configurar IAM na conta."],
                  "Não é boundary forte de segurança, combine com NetworkPolicy + RBAC para isolar.",
                  statement_en="A Namespace is used to:",
                  correct_en="Logically isolate resources within the cluster.",
                  wrong_en=["Replace the need to configure a VPC in the cloud.", "Only organize RBAC rules in the cluster.", "Replace the need to configure IAM on the account."],
                  explanation_en="Not a strong security boundary; combine with NetworkPolicy + RBAC to isolate."),
                q("Probe (liveness/readiness):",
                  "Indica saúde e prontidão do pod.",
                  ["Substitui a necessidade de configurar um Service.", "Aumenta automaticamente o número de réplicas do pod.", "Apaga o pod assim que ele reporta uma falha."],
                  "Liveness reinicia container. Readiness controla recebimento de tráfego.",
                  statement_en="A Probe (liveness/readiness):",
                  correct_en="Indicates the pod's health and readiness.",
                  wrong_en=["Replaces the need to configure a Service.", "Automatically increases the pod's replica count.", "Deletes the pod as soon as it reports a failure."],
                  explanation_en="Liveness restarts the container. Readiness controls whether it receives traffic."),
                q("Argo CD entrega via:",
                  "GitOps, sincroniza estado com Git.",
                  ["Entrega feita manualmente por alguém do time.", "Entrega feita por transferência de arquivos via FTP.", "Entrega agendada rodando via um job de cron."],
                  "Argo monitora repo; aplica diff continuamente. Drift é corrigido automaticamente.",
                  statement_en="Argo CD delivers via:",
                  correct_en="GitOps, syncing state with Git.",
                  wrong_en=["Delivery done manually by someone on the team.", "Delivery done by transferring files via FTP.", "Delivery scheduled to run via a cron job."],
                  explanation_en="Argo watches the repo; applies the diff continuously. Drift is corrected automatically."),
            ],
        },
        # =====================================================================
        # 5.2 K8s Hardening
        # =====================================================================
        {
            "title": "K8s Hardening",
            "title_en": "K8s Hardening",
            "summary": "Blindar o cluster contra invasões.",
            "summary_en": "Shielding the cluster against intrusions.",
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
                "intro_en": (
                    "K8s by default isn't secure, it's flexible. In its default configuration a pod "
                    "can run as root, mount the host filesystem, open a privileged socket, "
                    "and talk to any other pod in the cluster. Hardening is the work of "
                    "turning that flexibility into a defensible posture. The mandatory "
                    "references are the CIS Kubernetes Benchmark and the NSA/CISA Kubernetes Hardening "
                    "Guidance, read both at least once. This topic covers the "
                    "highest-impact controls."
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
<div class="mermaid">
flowchart LR
    User["Usuário / ServiceAccount"] --> Binding["RoleBinding"]
    Binding --> Role["Role: lista de permissões"]
    Role --> Resource["Recurso do cluster"]
</div>


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
                "body_en": (
                """<h3>1. The threat model: what hardening actually defends against</h3>
<p>Applying a hardening checklist without understanding what it prevents
produces a false sense of security — the right list only makes sense
when you know which of the five scenarios below it closes off. The
<strong>external attacker</strong> typically starts by exploiting a
vulnerability in the web application, uses that to compromise the container,
and from there tries to escalate to the node and then to the entire cluster
— every layer of hardening in this lesson exists to block one of those
jumps. The <strong>insider</strong> doesn't need any exploit at all: it's a
developer with <code>kubectl</code> trying to access a namespace they
shouldn't, or a CI token with a broader scope than the task
requires. <strong>Container breakout</strong> exploits a flaw in the runtime
or the kernel to escape container isolation and act directly
on the host — the scenario securityContext and seccomp (section 4) most
directly mitigate. <strong>Supply chain</strong> is a malicious
image pulled from a public registry, compromising the cluster before
the first deploy even happens. And <strong>misconfiguration</strong> —
an exposed Secret, overly permissive RBAC, encryption never
enabled — is, in practice, the biggest real source of incidents, far more
common than any sophisticated exploit. No single control
solves all five: hardening works as defense in layers, where
each layer covers what the previous one let through.</p>
<div class="mermaid">
flowchart LR
    User["Usuário / ServiceAccount"] --> Binding["RoleBinding"]
    Binding --> Role["Role: lista de permissões"]
    Role --> Resource["Recurso do cluster"]
</div>


<h3>2. Granular RBAC: four objects, and the verb that overrides all the others</h3>
<p>RBAC controls WHO can do WHAT on the Kubernetes API, through
four types of object: <code>Role</code> defines permissions within ONE
namespace; <code>ClusterRole</code> defines permissions spanning the
entire cluster or resources that don't belong to any namespace (Node,
PersistentVolume); <code>RoleBinding</code> connects a Role to a
specific user, group, or ServiceAccount; <code>ClusterRoleBinding</code>
does the same for a ClusterRole:</p>
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
<p>Best practice is to reserve <code>cluster-admin</code> for
emergency ("break-glass") access protected by MFA only, not as
a routine permission — for applications, granting LESS than seems
necessary at first and expanding only when a real permission error
shows up is safer than the reverse path. <code>kubectl auth can-i
--list --as=system:serviceaccount:ns:sa</code> audits exactly what
a ServiceAccount can do, without manually reading every Role and
Binding. Three verbs deserve extra attention:
<code>create</code>/<code>delete</code> for being destructive, and
especially <code>impersonate</code> — which lets whoever holds it act
AS any other user or ServiceAccount, effectively bypassing
the rest of the configured RBAC. And controlling just the verbs isn't enough:
whoever has permission to CREATE Roles with broad powers can escalate their
own privilege by creating a new, more permissive Role — which is why
whoever administers RBAC needs to be a distinct set of people from those who
just use the cluster day to day.</p>

<h3>3. Pod Security Standards: the PSP replacement, in three levels</h3>
<p>After PodSecurityPolicy (PSP) was removed, Kubernetes started
using Pod Security Standards (PSS), applied via namespace LABEL, with
three progressive levels of strictness. <strong>privileged</strong> imposes
no restriction at all — reserved for the cluster's own
infrastructure, not application workloads. <strong>baseline</strong>
blocks the most obvious and dangerous things (privileged containers, hostPID,
hostNetwork, hostPath) but still allows some flexibility — suitable
for a development environment. <strong>restricted</strong> is the
state of the art: it requires <code>runAsNonRoot</code>, dropping all
Linux capabilities by default, a defined seccomp profile, a
read-only root filesystem — the expected level in production:</p>
<pre><code>kubectl label ns prod \\
  pod-security.kubernetes.io/enforce=restricted \\
  pod-security.kubernetes.io/enforce-version=latest \\
  pod-security.kubernetes.io/warn=restricted \\
  pod-security.kubernetes.io/audit=restricted</code></pre>
<p>The three modes serve different purposes: <code>enforce</code>
actually BLOCKS a pod that violates the policy; <code>warn</code>
warns at the moment of <code>kubectl apply</code> without blocking it (useful during
a gradual migration to a stricter policy); <code>audit</code>
only logs the violation to the audit log, without interrupting anything — the
combination of the three lets you run in "observe before blocking" mode
before actually turning on enforcement. For finer-grained rules than
PSS natively covers, tools like Kyverno and OPA Gatekeeper (covered
in the Admission Controllers topic) fill the gap.</p>

<h3>4. `securityContext`: why each flag exists to close a specific vector</h3>
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
<p><code>runAsNonRoot</code> matters because UID 0 inside the container
is still UID 0 on the host (unless user namespaces, still in alpha
in Kubernetes 1.30, are enabled) — a container breakout running as
root inherits root on the entire host.
<code>readOnlyRootFilesystem</code> forces the application to use
specific volumes for any writes, which means an attacker who
compromises the process can't simply write a
malicious binary to <code>/usr/bin</code> — there's nowhere to write to.
<code>allowPrivilegeEscalation: false</code> specifically blocks the
technique of escalating privilege through a setuid binary.
Dropping ALL Linux capabilities by default acknowledges that
most web applications don't even need <code>NET_RAW</code> —
adding back only the strictly necessary capability (like
<code>NET_BIND_SERVICE</code> to listen on a privileged port)
keeps the surface minimal. And <code>seccompProfile: RuntimeDefault</code>
filters around 70 syscalls considered dangerous (like
<code>mount</code> and <code>ptrace</code>), reducing what a
compromised process inside the container can ask of the kernel, even if it has
already managed to execute arbitrary code.</p>

<h3>5. Default-deny NetworkPolicy: the minimum to avoid leaving the whole cluster open</h3>
<p>With no NetworkPolicy configured at all, compromising ONE pod gives network
access to ANY other pod in the cluster — there's no segmentation
by default. The minimum viable step is to deny everything and explicitly
allow what's necessary:</p>
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
<p>The detail easy to forget: a default-deny without the DNS
exception breaks name resolution for EVERY pod in the namespace — the
application stops working in a way that looks like a random network bug, when
in fact the policy is working exactly as configured, just
without the necessary exception. The dedicated Network Policies topic details
more advanced segmentation patterns; the essential point here is
simple: turn on default-deny, always.</p>

<h3>6. Encryption at rest: why "base64" isn't encryption</h3>
<p>etcd holds the entire cluster state, including Secrets and
ConfigMaps — and without encryption at rest configured, a dump of etcd
exposes ALL of the cluster's secrets in essentially readable text
(Secrets are base64-encoded by default, a REVERSIBLE
encoding with no key at all, not a real cryptographic
protection). Configuring this on the kube-apiserver closes that gap:</p>
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
<p>In managed clusters (EKS, GKE, AKS), enabling this protection
is usually a single "KMS encryption" option at cluster creation.
In a self-hosted cluster, it requires explicitly configuring a KMS plugin or
using the <code>aescbc</code> provider with a key you manage
yourself — without this manual configuration, the default behavior
remains the less secure one.</p>

<h3>7. Audit log: the only source that reconstructs "who did what, when"</h3>
<p>The audit log records every call made to the Kubernetes API — without
it, investigating a cluster security incident means having
no reliable record of what actions were taken before, during, and
after:</p>
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
<p>The policy above illustrates a deliberate trade-off: logging the full
BODY (<code>RequestResponse</code>) only for sensitive resources like
Secrets — enough to know exactly what changed — while the
rest of the traffic generates only metadata (who, when, which verb), without
the cost of storing and processing the full volume of every API call.
Sending this log to an external SIEM (Splunk, Datadog, ELK) is essential:
on managed cloud, it usually already flows automatically to
CloudWatch or Cloud Logging, but self-hosted requires configuring
that forwarding manually.</p>

<h3>8. ServiceAccount tokens: the vector most people forget to close</h3>
<p>By default, EVERY pod automatically mounts the <code>default</code>
ServiceAccount's token at
<code>/var/run/secrets/kubernetes.io/serviceaccount/</code> — even pods
that never need to talk to the Kubernetes API. An attacker who
compromises that pod finds this token ready to use, and from it
can make API calls with whatever permission the <code>default</code>
ServiceAccount has. The mitigation has three layers: for pods that
DON'T need to talk to the API, explicitly turn off auto-mount
(<code>automountServiceAccountToken: false</code>); for pods that
do need it, use a DEDICATED ServiceAccount with minimal RBAC, never the
shared <code>default</code>; and starting with Kubernetes 1.21,
"bound tokens" with a short TTL and tied to a specific
audience already come enabled by default on new ServiceAccounts, reducing
the window of use for a leaked token:</p>
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

<h3>9. Image hardening: reducing what exists to exploit</h3>
<p>Pinning images by digest (<code>@sha256:...</code>) instead of a
mutable tag guarantees that the same deploy always pulls exactly the same
content — a tag like <code>latest</code> might point to a
different image tomorrow, with no control over what changed. Using
distroless, chainguard, or wolfi base images eliminates the shell and
extra packages from the final image — an attacker who gains code execution
inside a shell-less container can't even exploit basic
system tools that simply don't exist there. Continuous scanning right in the
registry (Trivy, Grype, ECR/GAR Scanning) detects a new vulnerability
published AFTER the image was already built, not just at
build time. Verifying signatures (Cosign, applied via an admission webhook)
ensures that only images from authorized sources run on the cluster. And
attaching an SBOM documents exactly what makes up each
image, essential when a new vulnerability is announced and the
question is "which of our systems use that component?".</p>

<h3>10. Multi-tenancy: why namespace alone doesn't isolate anything real</h3>
<p>Namespace is an ORGANIZATIONAL boundary, not a strong
SECURITY boundary — two tenants sharing a cluster only via
separate namespaces, with nothing else, still share the same kernel,
the same control plane, and potentially the same nodes. Real
isolation requires additional layers: per-namespace RBAC controls who
administers what; default-deny NetworkPolicy per namespace prevents
cross-tenant traffic; ResourceQuota limits CPU, RAM, and object
count per namespace — without it, a badly behaved (or
compromised) tenant can consume enough resources to affect all the
others; LimitRange defines default request/limit values when a pod
doesn't declare its own; PSS restricted closes off the container surface;
node isolation via taints, tolerations, and nodeSelector puts each
tenant on dedicated physical nodes, the strongest layer available within
the same cluster; and Hierarchical Namespaces (HNC) organizes this at
scale for a large organization with many teams. For GENUINELY
hostile tenants — the case of a multi-customer PaaS where one
customer might be an adversary of another — the correct answer is a
dedicated cluster per tenant, not a namespace: no combination of controls
within a single cluster offers the same isolation guarantee that
physically separate clusters do.</p>

<h3>11. Automated auditing: measuring drift before it becomes an incident</h3>
<p><strong>kube-bench</strong> evaluates the cluster directly against the CIS
Kubernetes Benchmark — running it as a nightly CronJob and automatically opening a
ticket for any high-severity finding turns
compliance from a stressful annual event into a continuous, cheap
check. <strong>kubescape</strong> broadens coverage by combining NSA/CISA,
MITRE ATT&CK, and CIS in a friendlier interface.
<strong>Trivy K8s</strong> adds scanning of manifests, RBAC, and workloads
actually running in the cluster. <strong>kubeaudit</strong> and
<strong>polaris</strong> do static manifest linting before
the deploy even happens. And Falco/Tetragon (detailed in the Runtime
Security topic) cover the layer none of these static tools
reach: behavior observed at runtime, not declared configuration.</p>
<pre><code># Exemplo: rode kube-bench em CronJob
$ kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
$ kubectl logs job/kube-bench</code></pre>

<h3>12. The API server: protecting the single point that controls everything else</h3>
<p>The API server is the entire cluster's "castle" — compromising it
gives control over everything else. Keeping access via a private
endpoint, never exposed directly to the public internet, eliminates the
most obvious attack surface. Using OIDC for human authentication (integrated
with Google Workspace, Okta, Azure AD) centralizes identity in an already
audited provider, instead of managing isolated Kubernetes credentials. MFA should be
mandatory at the identity PROVIDER, not just assumed — protecting
only the local kubeconfig file doesn't prevent the use of a stolen
credential if the identity provider itself doesn't require a second factor. Binding
the kubeconfig to each person's laptop, with a short TTL and renewal via
OIDC, limits the window of use for a leaked credential. And for
SSH access to the nodes themselves, prefer managed mechanisms (SSM on AWS, IAP
on GCP) over static SSH keys; in a self-hosted environment, a bastion host
with an ed25519 key and second factor on the bastion itself is the minimum
acceptable.</p>

<h3>13. Backup and disaster recovery: a snapshot no one has restored yet isn't a backup</h3>
<p>A daily etcd snapshot (<code>etcdctl snapshot save
snap.db</code>) in a secure location is the basis of any disaster
recovery — without it, losing etcd means losing the entire
cluster state. Velero complements this by backing up Kubernetes
objects and persistent volumes, with the ability to restore even into a
DIFFERENT cluster than the original. The most frequently forgotten part:
actually testing the restore, periodically — a backup never restored
is an optimistic assumption, not a guarantee, for exactly the same
reason that a runbook never tested (seen in the Incident Response lesson)
has a good chance of being wrong exactly when it's needed.</p>

<h3>14. Five anti-patterns that show up with uncomfortable frequency</h3>
<ul>
<li><strong>Everything cluster-admin for CI</strong>: compromising the
CI pipeline, an increasingly targeted target, is equivalent to compromising
the entire cluster.</li>
<li><strong>default ServiceAccount with a broad RoleBinding</strong>:
any random pod inherits administrator privilege with no
specific configuration having to exist.</li>
<li><strong>No audit-log configured</strong>: when the incident
happens, there's no record at all to reconstruct what actually occurred.</li>
<li><strong>"We'll do hardening later"</strong>: a security technical
debt that only grows as the cluster gains more workloads,
more teams, more surface area.</li>
<li><strong>kube-bench run once, manually</strong>: any
improvement measured this way regresses over time (configuration drift)
without anyone noticing — only continuous automation sustains the gain.</li>
</ul>

<h3>15. Pragmatic roadmap, in order of impact per effort</h3>
<ol>
<li>Review who currently has <code>cluster-admin</code> and reduce it
aggressively — usually the highest-impact, lowest-effort
action.</li>
<li>Apply PSS restricted to production namespaces.</li>
<li>Turn on default-deny NetworkPolicy.</li>
<li>Enable encryption at rest on etcd.</li>
<li>Configure full securityContext on all Deployments.</li>
<li>Run kube-bench in nightly CI, with an automatic ticket for
high-severity findings.</li>
<li>Forward the audit log to a SIEM.</li>
<li>Add image scanning and signature verification to the pipeline.</li>
<li>Deploy runtime security (Falco), the layer that closes what
everything else, being static, can't reach.</li>
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
                "practical_en": (
                    "On a local cluster, run <code>kube-bench run --targets master,node</code>. "
                    "Identify 3 High findings and fix them (e.g., <code>--anonymous-auth=false</code>). "
                    "Apply the <code>pod-security.kubernetes.io/enforce=restricted</code> label to "
                    "a namespace and try to deploy a pod with <code>privileged: true</code>, "
                    "confirm it's rejected. Finally, create a Deployment with a full securityContext "
                    "(runAsNonRoot, readOnlyRootFilesystem, drop ALL caps) and debug the errors until "
                    "it runs clean."
                ),
            },
            "materials": [
                m("CIS Kubernetes Benchmark", "https://www.cisecurity.org/benchmark/kubernetes", "docs", "", title_en="CIS Kubernetes Benchmark", description_en=""),
                m("kube-bench", "https://github.com/aquasecurity/kube-bench", "tool", "", title_en="kube-bench", description_en=""),
                m("Pod Security Standards", "https://kubernetes.io/docs/concepts/security/pod-security-standards/", "docs", "", title_en="Pod Security Standards", description_en=""),
                m("RBAC docs", "https://kubernetes.io/docs/reference/access-authn-authz/rbac/", "docs", "", title_en="RBAC docs", description_en=""),
                m("NSA/CISA Kubernetes Hardening Guide", "https://www.cisa.gov/sites/default/files/publications/Kubernetes_Hardening_Guide_1.2.pdf", "docs", "", title_en="NSA/CISA Kubernetes Hardening Guide", description_en=""),
                m("Kubescape", "https://kubescape.io/", "tool", "Validação CIS + NSA.", title_en="Kubescape", description_en="CIS + NSA validation."),
                m("Trivy K8s", "https://aquasecurity.github.io/trivy/latest/docs/target/kubernetes/", "tool", "", title_en="Trivy K8s", description_en=""),
            ],
            "questions": [
                q("RBAC em K8s:",
                  "Concede permissões via Roles/ClusterRoles + Bindings.",
                  ["Substitui a necessidade de ter um cluster configurado.", "Concede permissão só para os nodes do cluster.", "Concede permissão só para pods rodando no cluster."],
                  "Aplique para SAs (apps), usuários e grupos. Audit com kubectl auth can-i.",
                  statement_en="RBAC in K8s:",
                  correct_en="Grants permissions via Roles/ClusterRoles + Bindings.",
                  wrong_en=["Replaces the need to have a cluster configured.", "Grants permission only to the cluster's nodes.", "Grants permission only to pods running in the cluster."],
                  explanation_en="Apply it to SAs (apps), users, and groups. Audit with kubectl auth can-i."),
                q("PodSecurity 'restricted':",
                  "Política mais segura disponível por padrão.",
                  ["Uma política que só funciona dentro do GKE do Google.", "Uma política que permite root com muita facilidade.", "Uma política que praticamente não oferece proteção real."],
                  "Bloqueia hostPath, privileged, runAsRoot, hostNetwork, hostPID etc.",
                  statement_en="PodSecurity 'restricted':",
                  correct_en="The most secure policy available by default.",
                  wrong_en=["A policy that only works inside Google's GKE.", "A policy that allows root all too easily.", "A policy that offers practically no real protection."],
                  explanation_en="Blocks hostPath, privileged, runAsRoot, hostNetwork, hostPID, etc."),
                q("NetworkPolicy default deny:",
                  "Boa prática para limitar tráfego inter-pods.",
                  ["Aumenta bastante o uso de CPU consumido pelo cluster.", "Apaga automaticamente os pods afetados pela regra.", "Bloqueia completamente grande parte do tráfego do cluster."],
                  "Sem NP, qualquer pod compromisso vira pivot para todo o cluster.",
                  statement_en="Default-deny NetworkPolicy:",
                  correct_en="Good practice for limiting pod-to-pod traffic.",
                  wrong_en=["Significantly increases the cluster's CPU usage.", "Automatically deletes the pods affected by the rule.", "Completely blocks most of the cluster's traffic."],
                  explanation_en="Without NP, any compromised pod becomes a pivot into the entire cluster."),
                q("Secrets em etcd:",
                  "Devem ser criptografados em repouso (KMS).",
                  ["Só precisam ser criptografados já em produção.", "Já vêm criptografados por padrão em qualquer cluster.", "Não fazem muita diferença para a segurança do cluster."],
                  "Por padrão, Secret é só base64 no etcd. Configure EncryptionConfiguration.",
                  statement_en="Secrets in etcd:",
                  correct_en="Should be encrypted at rest (KMS).",
                  wrong_en=["Only need to be encrypted once already in production.", "Already come encrypted by default in any cluster.", "Don't make much difference to the cluster's security."],
                  explanation_en="By default, a Secret is just base64 in etcd. Configure EncryptionConfiguration."),
                q("Audit logs em K8s:",
                  "Registram ações na API server.",
                  ["Registram ações só relacionadas diretamente a Pods.", "Substituem a necessidade de coletar métricas do cluster.", "Registram só informações de resolução de DNS."],
                  "Configure política em audit-policy.yaml e envie para SIEM externo.",
                  statement_en="Audit logs in K8s:",
                  correct_en="Record actions taken on the API server.",
                  wrong_en=["Only record actions directly related to Pods.", "Replace the need to collect metrics from the cluster.", "Only record DNS resolution information."],
                  explanation_en="Configure the policy in audit-policy.yaml and send it to an external SIEM."),
                q("kube-bench faz:",
                  "Avalia cluster contra CIS Benchmark.",
                  ["Atualiza automaticamente a versão de cada node.", "Substitui a necessidade de configurar RBAC no cluster.", "Aplica patches de segurança diretamente nos nodes."],
                  "Rode periodicamente; integre saída ao CI/CD para barrar merges sem fix.",
                  statement_en="kube-bench does:",
                  correct_en="Evaluates the cluster against the CIS Benchmark.",
                  wrong_en=["Automatically updates each node's version.", "Replaces the need to configure RBAC in the cluster.", "Applies security patches directly to the nodes."],
                  explanation_en="Run it periodically; integrate its output into CI/CD to block merges without a fix."),
                q("ServiceAccount default:",
                  "Não deve montar token automaticamente em todo pod.",
                  ["Substitui a necessidade de configurar IAM na conta.", "Já vem sem algum tipo de token por padrão.", "Deve montar o token automaticamente em cada pod criado."],
                  "Set `automountServiceAccountToken: false` quando o pod não precisa falar com API.",
                  statement_en="The default ServiceAccount:",
                  correct_en="Should not automatically mount a token in every pod.",
                  wrong_en=["Replaces the need to configure IAM on the account.", "Already comes without any kind of token by default.", "Should mount the token automatically in every pod created."],
                  explanation_en="Set `automountServiceAccountToken: false` when the pod doesn't need to talk to the API."),
                q("Cluster admin:",
                  "Restringir uso a engenheiros estritos com MFA.",
                  ["Uma permissão que praticamente não precisa de controle.", "Um acesso que deveria ser concedido a grande parte do time.", "Um acesso reservado só para pipelines de CI."],
                  "Cluster-admin é equivalente a root no cluster. Acesso break-glass auditado.",
                  statement_en="Cluster admin:",
                  correct_en="Restrict its use to a strict set of engineers with MFA.",
                  wrong_en=["A permission that practically needs no control at all.", "An access level that should be granted to most of the team.", "An access level reserved only for CI pipelines."],
                  explanation_en="Cluster-admin is equivalent to root on the cluster. Audited break-glass access."),
                q("Image pull secret:",
                  "Permite pull de registry privado.",
                  ["Só cuida da resolução de nomes DNS do cluster.", "Substitui a necessidade de configurar RBAC no cluster.", "Apaga imagens antigas guardadas no registry."],
                  "Configure em SA da app via imagePullSecrets. Em cloud, IRSA/Workload Identity > secret estático.",
                  statement_en="An image pull secret:",
                  correct_en="Allows pulling from a private registry.",
                  wrong_en=["Only handles DNS name resolution for the cluster.", "Replaces the need to configure RBAC in the cluster.", "Deletes old images stored in the registry."],
                  explanation_en="Configure it on the app's SA via imagePullSecrets. In the cloud, IRSA/Workload Identity beats a static secret."),
                q("Container privilegiado:",
                  "Tem ~root no host, evite ao máximo.",
                  ["Um recurso necessário na grande maioria dos deploys.", "Um recurso considerado mais seguro que o padrão.", "Um recurso que deixa os pods rodando mais rápido."],
                  "Apenas casos justificados (CNI agent, GPU driver). Bloqueie em policy padrão.",
                  statement_en="A privileged container:",
                  correct_en="Has near-root on the host, avoid it as much as possible.",
                  wrong_en=["A feature required in the vast majority of deploys.", "A feature considered more secure than the default.", "A feature that makes pods run faster."],
                  explanation_en="Only for justified cases (CNI agent, GPU driver). Block it by default in policy."),
            ],
        },
        # =====================================================================
        # 5.3 Network Policies
        # =====================================================================
        {
            "title": "Network Policies",
            "title_en": "Network Policies",
            "summary": "Controlar quem fala com quem dentro do cluster.",
            "summary_en": "Control who talks to whom inside the cluster.",
            "lesson": {
                "intro": (
                    "Em K8s default, todo pod conversa com todo pod. NetworkPolicy muda isso. "
                    "Sem NP, comprometer um pod = pivotar livremente pelo cluster, cenário "
                    "clássico de movimento lateral em quase todo breach reportado em K8s. "
                    "NetworkPolicy é o firewall L3/L4 do cluster, declarativo e por label. "
                    "Aprender a escrevê-las bem é uma das maiores alavancas de defesa."
                ),
                "intro_en": (
                    "In default K8s, every pod talks to every pod. NetworkPolicy changes that. Without NP, "
                    "compromising one pod = pivoting freely across the cluster, the classic lateral-movement "
                    "scenario in almost every reported K8s breach. NetworkPolicy is the cluster's L3/L4 "
                    "firewall, declarative and label-based. Learning to write them well is one of the biggest "
                    "defense levers."
                ),
                "body": (
                """<h3>1. NetworkPolicy é só um objeto — quem de fato aplica é o CNI</h3>
<p>Um detalhe que confunde muita gente na primeira vez: NetworkPolicy é
um objeto Kubernetes comum, aceito pelo API server e gravado no etcd
como qualquer outro recurso — mas o API server NUNCA aplica a regra em
si. Quem efetivamente FAZ a política valer é o plugin CNI instalado no
cluster. Se o CNI em uso não suporta NetworkPolicy (kubenet padrão, ou
flannel sem um add-on específico), o objeto se torna literalmente
decorativo: existe no etcd, aparece no <code>kubectl get</code>, mas
nenhum pacote é de fato bloqueado — um risco silencioso, porque o time
pode acreditar que está protegido só por ter aplicado o YAML. Em
produção, use um CNI que implemente NetworkPolicy de verdade — Calico,
Cilium, Antrea ou Weave. Por baixo dos panos, o CNI traduz a política
declarativa em regras de iptables, ipvs ou eBPF (dependendo da
implementação) — um detalhe que você não precisa gerenciar diretamente,
só saber que precisa estar presente.</p>
<div class="mermaid">
flowchart LR
    subgraph SemNP ["Sem NetworkPolicy"]
        A1["Pod A"] --> B1["Pod B"]
        A1 --> C1["Pod C"]
    end
    subgraph ComNP ["Com default-deny + regra explícita"]
        A2["Pod A"] --> B2["Pod B, permitido"]
    end
</div>


<h3>2. Anatomia de uma política: seletor, direção, e o que cada campo decide</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-web
  namespace: prod
spec:
  podSelector:
    matchLabels: { app: api }       # quem é alvo desta política
  policyTypes: [Ingress, Egress]    # qual direção
  ingress:
  - from:
    - podSelector:
        matchLabels: { app: web }   # quem pode entrar
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels: { kubernetes.io/metadata.name: kube-system }
      podSelector:
        matchLabels: { k8s-app: kube-dns }
    ports:
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels: { app: postgres }
    ports:
    - protocol: TCP
      port: 5432</code></pre>
<p>Um <code>podSelector: {}</code> vazio significa TODOS os pods do
namespace, não "nenhum" — uma inversão que confunde quem espera lógica
de lista vazia = vazio. NetworkPolicy é ADITIVA: quando várias políticas
atingem o mesmo pod, os efeitos se SOMAM — não existe conceito de
prioridade ou de uma política "vencer" outra; se QUALQUER política
permite um fluxo específico, esse fluxo é permitido, mesmo que outra
política mais restritiva também exista. O comportamento padrão inverte
dependendo de existir ou não alguma política visando aquele pod: sem
NENHUMA NetworkPolicy atingindo um pod, tudo é permitido livremente; no
momento em que QUALQUER política passa a atingir esse pod, o padrão vira
negar tudo, exceto o que essa política explicitamente permitir. E
NetworkPolicy padrão opera nas camadas 3 e 4 (endereço IP e porta) — para
controle na camada 7 (caminho HTTP específico, método), é preciso Cilium
Network Policies (seção 7) ou um service mesh completo.</p>

<h3>3. Default-deny por namespace: o ponto de partida de qualquer segmentação séria</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
# sem `ingress` nem `egress` = nada é permitido</code></pre>
<p>Aplicada sozinha, essa política bloqueia absolutamente TUDO — inclusive
resolução de DNS, telemetria e acesso ao registry de imagens — porque
"nada especificado" significa "nada permitido" quando a política já
está atingindo o pod. É deliberadamente o ponto de partida mais
restritivo possível: a partir daqui, cada exceção necessária é adicionada
explicitamente, em vez de começar permissivo e tentar identificar depois
o que deveria ter sido bloqueado.</p>

<h3>4. A primeira exceção que todo mundo esquece: DNS</h3>
<p>Um pod sem egress liberado para o kube-dns simplesmente não resolve
NENHUM nome — o sintoma característico é a aplicação reclamando "Name or
service not known" em toda tentativa de conexão, um erro que parece de
configuração de aplicação mas na verdade é a NetworkPolicy funcionando
exatamente como configurada:</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector:
        matchLabels: { kubernetes.io/metadata.name: kube-system }
      podSelector:
        matchLabels: { k8s-app: kube-dns }
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53</code></pre>
<p>Essa exceção é praticamente universal — todo namespace com
default-deny precisa dela, porque nenhuma aplicação moderna funciona sem
resolução de nome funcionando.</p>

<h3>5. Seletores: onde AND e OR se confundem por causa da indentação</h3>
<p>Existem quatro formas de "casar" um destino ou origem numa
NetworkPolicy: <code>podSelector</code> filtra por label do pod (dentro
do mesmo namespace); <code>namespaceSelector</code> filtra por label do
NAMESPACE; a combinação dos dois DENTRO do mesmo elemento da lista
funciona como AND (label do pod E label do namespace, ambos
simultaneamente); e <code>ipBlock</code> filtra por faixa CIDR,
geralmente usado para egress a destinos externos ao cluster. A
combinatória crítica, e fonte comum de erro, está em como o YAML é
estruturado:</p>
<pre><code>ingress:
- from:
  - namespaceSelector: { matchLabels: { env: prod } }
    podSelector: { matchLabels: { app: web } }
# regra acima: pod E ns combinados (AND)

ingress:
- from:
  - namespaceSelector: { matchLabels: { env: prod } }
  - podSelector: { matchLabels: { app: web } }
# regra acima: pod OU ns (OR, dois itens da lista from)</code></pre>
<p>A diferença entre as duas versões é APENAS onde o traço (<code>-</code>)
de item de lista aparece — no primeiro caso, os dois seletores estão
dentro do MESMO item da lista <code>from</code> (portanto AND); no
segundo, são dois itens SEPARADOS da lista (portanto OR, "casa com
qualquer um dos dois"). É um erro fácil de cometer justamente porque a
diferença visual no YAML é sutil, e o efeito prático — uma regra
pretendida restritiva (AND) que na verdade ficou permissiva (OR) — só
aparece testando de verdade, nunca só lendo o arquivo.</p>

<h3>6. Egress: o controle que a maioria ignora, e onde mora o valor real</h3>
<p>Toda política de Ingress que todo mundo escreve por padrão — mas
Egress é onde a segurança de verdade se ganha, e é sistematicamente
menos escrita. Um pod comprometido SEM egress controlado pode fazer três
coisas perigosas livremente: exfiltrar dados para um servidor de
comando-e-controle externo, pivotar lateralmente para outros pods do
mesmo cluster, e baixar malware adicional de um registry público
qualquer. Bloquear egress por padrão fecha as três portas de uma vez. A
estratégia em camadas: primeiro default-deny de egress; depois liberar
DNS (seção 4); depois liberar destinos internos especificamente
necessários (banco, cache, outros serviços que a aplicação de fato
chama); e para acesso à internet propriamente dito, rotear através de um
proxy de saída dedicado (Squid, ou uma solução ZTNA) que aplica uma
allowlist explícita de domínios e gera log auditável de cada conexão —
em vez de liberar egress irrestrito para qualquer destino externo:</p>
<pre><code># exemplo: pod web só fala com api e DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: web-egress, namespace: prod }
spec:
  podSelector: { matchLabels: { app: web } }
  policyTypes: [Egress]
  egress:
  - to:
    - podSelector: { matchLabels: { app: api } }
    ports: [{ protocol: TCP, port: 8080 }]
  - to:
    - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
      podSelector: { matchLabels: { k8s-app: kube-dns } }
    ports: [{ protocol: UDP, port: 53 }]</code></pre>

<h3>7. Cilium Network Policies: quando bloquear por IP e porta não basta</h3>
<p>Cilium estende a NetworkPolicy padrão para camada 7 — HTTP, gRPC,
Kafka, DNS — e permite casar tráfego por identidade SPIFFE ou por nome de
domínio (FQDN), não só por IP:</p>
<pre><code>apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata: { name: api-l7, namespace: prod }
spec:
  endpointSelector: { matchLabels: { app: api } }
  ingress:
  - fromEndpoints:
    - matchLabels: { app: web }
    toPorts:
    - ports: [{ port: "8080", protocol: TCP }]
      rules:
        http:
        - method: GET
          path: "/api/v1/users"
        - method: GET
          path: "/api/v1/orders/[0-9]+"
  egress:
  - toFQDNs:
    - matchPattern: "*.googleapis.com"
    toPorts:
    - ports: [{ port: "443", protocol: TCP }]</code></pre>
<p>Essa política permite que "web" chame especificamente
<code>GET /api/v1/users</code> em "api", mas bloqueia
<code>DELETE</code> no mesmo caminho — uma granularidade que
NetworkPolicy padrão simplesmente não alcança, porque ela só enxerga até
a camada de porta TCP, sem noção do conteúdo HTTP por trás. Isso limita
o que um pod comprometido consegue fazer MESMO dentro de um fluxo de
rede já permitido — se "web" for comprometido, o atacante ainda não
consegue chamar operações destrutivas em "api" que a política L7
explicitamente não autoriza.</p>

<h3>8. Observabilidade: o ponto cego de NetworkPolicy por design</h3>
<p>Quando uma NetworkPolicy rejeita um pacote, ela faz isso
SILENCIOSAMENTE — o pacote simplesmente desaparece, sem nenhuma mensagem
de erro específica voltando para a aplicação. O sintoma na aplicação é
genérico ("connection refused" ou timeout), e sem ferramenta dedicada
não há como distinguir se a causa foi a NetworkPolicy, o kube-proxy, ou
a aplicação de destino simplesmente estar fora do ar. Cilium Hubble
resolve isso mostrando um stream em tempo real de fluxos permitidos e
negados, via CLI ou interface visual — a ferramenta certa para responder
"esse bloqueio é intencional ou é um bug de policy?" rapidamente. Calico
expõe logs equivalentes via Felix, configuráveis por verbosidade.
<code>tcpdump</code> rodando dentro do pod (via capability
<code>NET_ADMIN</code> ou um container efêmero de debug) confirma se o
pacote sequer sai da interface de rede. E um simples
<code>kubectl exec ... -- nc -zv host port</code> testa conectividade
pontual sem instrumentação adicional. A estratégia mais segura para
introduzir política nova é rodar primeiro em modo "audit-only" — Calico
tem uma flag específica para isso, Cilium usa
<code>policyEnforcementMode: never</code> — capturando o que SERIA
bloqueado antes de ativar o bloqueio de fato.</p>

<h3>9. Um padrão de implantação que não quebra produção no meio do caminho</h3>
<ol>
<li>Em um cluster novo, comece com políticas PERMISSIVAS
(<code>allow-all</code>) em todos os namespaces de produção — o objetivo
inicial é ter o mecanismo instalado, não bloquear nada ainda.</li>
<li>Namespace por namespace, substitua a política permissiva por
default-deny mais as regras especificamente necessárias.</li>
<li>Use Hubble ou os logs do Felix para confirmar que nada está sendo
bloqueado por engano antes de seguir adiante.</li>
<li>Avance para o próximo namespace só depois de validar o anterior.</li>
<li>Depois que todos os namespaces críticos estiverem estabilizados,
escreva uma policy de CI (via Kyverno ou Gatekeeper) exigindo que TODO
namespace de produção novo já nasça com default-deny — fechando a
lacuna de alguém esquecer de aplicar manualmente no futuro.</li>
</ol>

<h3>10. Tráfego para fora do cluster: CIDR estático vs. FQDN dinâmico</h3>
<pre><code>egress:
- to:
  - ipBlock:
      cidr: 10.0.0.0/8         # rede interna corporativa
      except: [10.0.99.0/24]   # exceto subnet sensível
  ports: [{ protocol: TCP, port: 443 }]</code></pre>
<p>NetworkPolicy padrão só sabe trabalhar com CIDR — uma limitação real
quando o destino é um serviço de nuvem cujo IP muda com frequência (S3,
uma API SaaS qualquer). Por isso o suporte a FQDN do Cilium
(<code>toFQDNs</code>, visto na seção 7) é mais robusto para esses
casos: a política acompanha o NOME do serviço, não um endereço IP
específico que pode mudar sem aviso.</p>

<h3>11. Os limites de NetworkPolicy: dentro de UM cluster, não entre vários</h3>
<p>NetworkPolicy opera inteiramente DENTRO de um único cluster — para
tráfego entre clusters diferentes (arquitetura multi-região ou
multi-nuvem), a ferramenta certa é um service mesh (Istio, Linkerd,
Cilium ClusterMesh) que estabelece identidade comum, mTLS e autorização
por carga de trabalho ATRAVÉS da fronteira de cluster, algo que
NetworkPolicy nativa simplesmente não alcança. A aula de Zero Trust
Architecture detalha esse cenário mais amplo.</p>

<h3>12. Seis anti-padrões que aparecem com frequência em auditorias</h3>
<ul>
<li><strong>Política só de ingress</strong>: deixa egress totalmente
livre, abrindo a porta de exfiltração que a seção 6 fecha.</li>
<li><strong>Esquecer a exceção de DNS</strong>: a aplicação quebra de
forma silenciosa e confusa, sem nenhuma mensagem apontando para a causa
real.</li>
<li><strong>Confundir AND com OR nos seletores</strong> (seção 5): uma
regra pretendida restritiva vira acidentalmente permissiva, sem nenhum
erro de sintaxe que denuncie o problema.</li>
<li><strong>CNI incompatível instalado</strong>: a política existe no
etcd mas não é enforçada por ninguém — o pior tipo de falha, porque
parece proteção mas não é.</li>
<li><strong>NetworkPolicy aplicada em `kube-system`</strong>: risco real
de quebrar DNS, o próprio CNI, ou o ingress controller — exige teste
cuidadoso antes de aplicar ali.</li>
<li><strong>Labels que ficam desatualizados após renomear a
aplicação</strong>: a NetworkPolicy referencia um label que já não
corresponde a nada, e o fluxo passa a ser bloqueado (ou liberado)
silenciosamente, sem ninguém ter mudado a política intencionalmente.</li>
</ul>

<h3>13. Validação automatizada: não depender de revisão manual de YAML</h3>
<p>O NetworkPolicy Editor (editor.networkpolicy.io) oferece uma
interface visual para conferir o efeito real de uma política antes de
aplicá-la — útil justamente para pegar o erro de AND/OR da seção 5 antes
que chegue a produção. Ferramentas como <code>cnp-checker</code> e
<code>kubectl-np-viewer</code> validam a lógica das regras
programaticamente. Kyverno ou Gatekeeper (vistos na aula de Admission
Controllers) podem forçar, via policy de admissão, que todo namespace
novo já nasça com default-deny, fechando a lacuna de alguém esquecer o
passo manual. E Hubble, além de servir para debug pontual (seção 8),
vale rodar continuamente em produção como validação contínua de que o
comportamento real da rede ainda corresponde ao que as políticas
declaram.</p>"""
                ),
                "body_en": (
                """<h3>1. NetworkPolicy is just an object — what actually enforces it is the CNI</h3>
<p>A detail that confuses many people the first time: NetworkPolicy is
a normal Kubernetes object, accepted by the API server and stored in etcd
like any other resource — but the API server NEVER applies the rule
itself. What actually MAKES the policy stick is the CNI plugin installed in
the cluster. If the CNI in use does not support NetworkPolicy (default kubenet, or
flannel without a specific add-on), the object becomes literally
decorative: it exists in etcd, shows up in <code>kubectl get</code>, but
no packet is actually blocked — a silent risk, because the team
may believe it is protected just by having applied the YAML. In
production, use a CNI that truly implements NetworkPolicy — Calico,
Cilium, Antrea, or Weave. Under the hood, the CNI translates the declarative
policy into iptables, ipvs, or eBPF rules (depending on the
implementation) — a detail you do not need to manage directly,
only know that it needs to be present.</p>
<div class="mermaid">
flowchart LR
    subgraph SemNP ["Sem NetworkPolicy"]
        A1["Pod A"] --> B1["Pod B"]
        A1 --> C1["Pod C"]
    end
    subgraph ComNP ["Com default-deny + regra explícita"]
        A2["Pod A"] --> B2["Pod B, permitido"]
    end
</div>


<h3>2. Anatomy of a policy: selector, direction, and what each field decides</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-web
  namespace: prod
spec:
  podSelector:
    matchLabels: { app: api }       # quem é alvo desta política
  policyTypes: [Ingress, Egress]    # qual direção
  ingress:
  - from:
    - podSelector:
        matchLabels: { app: web }   # quem pode entrar
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels: { kubernetes.io/metadata.name: kube-system }
      podSelector:
        matchLabels: { k8s-app: kube-dns }
    ports:
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels: { app: postgres }
    ports:
    - protocol: TCP
      port: 5432</code></pre>
<p>An empty <code>podSelector: {}</code> means ALL pods in the
namespace, not "none" — an inversion that confuses anyone expecting empty-list
logic = empty. NetworkPolicy is ADDITIVE: when several policies
hit the same pod, the effects ADD UP — there is no concept of
priority or of one policy "winning" over another; if ANY policy
allows a specific flow, that flow is allowed, even if another
more restrictive policy also exists. Default behavior flips
depending on whether some policy targets that pod: with
NO NetworkPolicy hitting a pod, everything is freely allowed; the
moment ANY policy starts hitting that pod, the default becomes
deny everything except what that policy explicitly allows. And
standard NetworkPolicy operates at layers 3 and 4 (IP address and port) — for
control at layer 7 (specific HTTP path, method), you need Cilium
Network Policies (section 7) or a full service mesh.</p>

<h3>3. Default-deny per namespace: the starting point of any serious segmentation</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
# sem `ingress` nem `egress` = nada é permitido</code></pre>
<p>Applied alone, this policy blocks absolutely EVERYTHING — including
DNS resolution, telemetry, and access to the image registry — because
"nothing specified" means "nothing allowed" when the policy is already
hitting the pod. It is deliberately the most restrictive starting
point possible: from here, every needed exception is added
explicitly, instead of starting permissive and trying to identify later
what should have been blocked.</p>

<h3>4. The first exception everyone forgets: DNS</h3>
<p>A pod without egress opened to kube-dns simply does not resolve
ANY name — the characteristic symptom is the application complaining "Name or
service not known" on every connection attempt, an error that looks like
application misconfiguration but is actually NetworkPolicy working
exactly as configured:</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector:
        matchLabels: { kubernetes.io/metadata.name: kube-system }
      podSelector:
        matchLabels: { k8s-app: kube-dns }
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53</code></pre>
<p>This exception is practically universal — every namespace with
default-deny needs it, because no modern application works without
working name resolution.</p>

<h3>5. Selectors: where AND and OR get confused because of indentation</h3>
<p>There are four ways to "match" a destination or source in a
NetworkPolicy: <code>podSelector</code> filters by pod label (within
the same namespace); <code>namespaceSelector</code> filters by
NAMESPACE label; combining both INSIDE the same list element
works as AND (pod label AND namespace label, both
at once); and <code>ipBlock</code> filters by CIDR range,
usually used for egress to destinations outside the cluster. The
critical combinatorics, and a common source of error, is in how the YAML is
structured:</p>
<pre><code>ingress:
- from:
  - namespaceSelector: { matchLabels: { env: prod } }
    podSelector: { matchLabels: { app: web } }
# regra acima: pod E ns combinados (AND)

ingress:
- from:
  - namespaceSelector: { matchLabels: { env: prod } }
  - podSelector: { matchLabels: { app: web } }
# regra acima: pod OU ns (OR, dois itens da lista from)</code></pre>
<p>The difference between the two versions is ONLY where the dash (<code>-</code>)
of the list item appears — in the first case, both selectors are
inside the SAME item of the <code>from</code> list (therefore AND); in
the second, they are two SEPARATE list items (therefore OR, "matches
either of the two"). It is an easy mistake precisely because the
visual difference in YAML is subtle, and the practical effect — a rule
meant to be restrictive (AND) that actually became permissive (OR) — only
shows up when you truly test, never just by reading the file.</p>

<h3>6. Egress: the control most people ignore, and where the real value lives</h3>
<p>Everyone writes Ingress policies by default — but
Egress is where real security is won, and it is systematically
written less. A compromised pod WITHOUT controlled egress can do three
dangerous things freely: exfiltrate data to an external
command-and-control server, pivot laterally to other pods in the
same cluster, and download additional malware from any public
registry. Blocking egress by default closes all three doors at once. The
layered strategy: first default-deny egress; then open
DNS (section 4); then open specifically necessary internal
destinations (database, cache, other services the application actually
calls); and for internet access proper, route through a
dedicated egress proxy (Squid, or a ZTNA solution) that applies an
explicit domain allowlist and produces an auditable log of every connection —
instead of opening unrestricted egress to any external destination:</p>
<pre><code># exemplo: pod web só fala com api e DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: web-egress, namespace: prod }
spec:
  podSelector: { matchLabels: { app: web } }
  policyTypes: [Egress]
  egress:
  - to:
    - podSelector: { matchLabels: { app: api } }
    ports: [{ protocol: TCP, port: 8080 }]
  - to:
    - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
      podSelector: { matchLabels: { k8s-app: kube-dns } }
    ports: [{ protocol: UDP, port: 53 }]</code></pre>

<h3>7. Cilium Network Policies: when blocking by IP and port is not enough</h3>
<p>Cilium extends standard NetworkPolicy to layer 7 — HTTP, gRPC,
Kafka, DNS — and lets you match traffic by SPIFFE identity or by domain
name (FQDN), not only by IP:</p>
<pre><code>apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata: { name: api-l7, namespace: prod }
spec:
  endpointSelector: { matchLabels: { app: api } }
  ingress:
  - fromEndpoints:
    - matchLabels: { app: web }
    toPorts:
    - ports: [{ port: "8080", protocol: TCP }]
      rules:
        http:
        - method: GET
          path: "/api/v1/users"
        - method: GET
          path: "/api/v1/orders/[0-9]+"
  egress:
  - toFQDNs:
    - matchPattern: "*.googleapis.com"
    toPorts:
    - ports: [{ port: "443", protocol: TCP }]</code></pre>
<p>This policy allows "web" to call specifically
<code>GET /api/v1/users</code> on "api", but blocks
<code>DELETE</code> on the same path — a granularity that
standard NetworkPolicy simply cannot reach, because it only sees up to
the TCP port layer, with no notion of the HTTP content behind it. That limits
what a compromised pod can do EVEN inside an already
allowed network flow — if "web" is compromised, the attacker still cannot
call destructive operations on "api" that the L7 policy
explicitly does not authorize.</p>

<h3>8. Observability: NetworkPolicy's blind spot by design</h3>
<p>When a NetworkPolicy rejects a packet, it does so
SILENTLY — the packet simply disappears, with no specific error
message returning to the application. The symptom in the application is
generic ("connection refused" or timeout), and without a dedicated tool
there is no way to tell whether the cause was NetworkPolicy, kube-proxy, or
the destination application simply being down. Cilium Hubble
solves this by showing a real-time stream of allowed and
denied flows, via CLI or visual UI — the right tool to answer
"is this block intentional or a policy bug?" quickly. Calico
exposes equivalent logs via Felix, configurable by verbosity.
<code>tcpdump</code> running inside the pod (via the
<code>NET_ADMIN</code> capability or an ephemeral debug container) confirms whether the
packet even leaves the network interface. And a simple
<code>kubectl exec ... -- nc -zv host port</code> tests point
connectivity without extra instrumentation. The safest strategy to
introduce a new policy is to run first in "audit-only" mode — Calico
has a specific flag for that, Cilium uses
<code>policyEnforcementMode: never</code> — capturing what WOULD BE
blocked before actually enabling the block.</p>

<h3>9. A rollout pattern that does not break production halfway</h3>
<ol>
<li>On a new cluster, start with PERMISSIVE policies
(<code>allow-all</code>) in all production namespaces — the initial
goal is to have the mechanism installed, not to block anything yet.</li>
<li>Namespace by namespace, replace the permissive policy with
default-deny plus the specifically needed rules.</li>
<li>Use Hubble or Felix logs to confirm nothing is being
blocked by mistake before moving on.</li>
<li>Advance to the next namespace only after validating the previous one.</li>
<li>After all critical namespaces are stabilized,
write a CI policy (via Kyverno or Gatekeeper) requiring that EVERY
new production namespace is born with default-deny — closing the
gap of someone forgetting to apply it manually in the future.</li>
</ol>

<h3>10. Traffic leaving the cluster: static CIDR vs. dynamic FQDN</h3>
<pre><code>egress:
- to:
  - ipBlock:
      cidr: 10.0.0.0/8         # rede interna corporativa
      except: [10.0.99.0/24]   # exceto subnet sensível
  ports: [{ protocol: TCP, port: 443 }]</code></pre>
<p>Standard NetworkPolicy only knows how to work with CIDR — a real limitation
when the destination is a cloud service whose IP changes often (S3,
any SaaS API). That is why Cilium's FQDN support
(<code>toFQDNs</code>, seen in section 7) is more robust for these
cases: the policy follows the service NAME, not a specific IP
address that can change without notice.</p>

<h3>11. NetworkPolicy limits: inside ONE cluster, not across several</h3>
<p>NetworkPolicy operates entirely INSIDE a single cluster — for
traffic between different clusters (multi-region or
multi-cloud architecture), the right tool is a service mesh (Istio, Linkerd,
Cilium ClusterMesh) that establishes shared identity, mTLS, and workload
authorization ACROSS the cluster boundary, something
native NetworkPolicy simply does not reach. The Zero Trust
Architecture lesson covers that broader scenario.</p>

<h3>12. Six anti-patterns that show up often in audits</h3>
<ul>
<li><strong>Ingress-only policy</strong>: leaves egress fully
open, opening the exfiltration door that section 6 closes.</li>
<li><strong>Forgetting the DNS exception</strong>: the application breaks in a
silent and confusing way, with no message pointing to the real
cause.</li>
<li><strong>Confusing AND with OR in selectors</strong> (section 5): a
rule meant to be restrictive accidentally becomes permissive, with no
syntax error to flag the problem.</li>
<li><strong>Incompatible CNI installed</strong>: the policy exists in
etcd but is enforced by nobody — the worst kind of failure, because
it looks like protection but is not.</li>
<li><strong>NetworkPolicy applied in `kube-system`</strong>: real risk
of breaking DNS, the CNI itself, or the ingress controller — requires careful
testing before applying there.</li>
<li><strong>Labels that go stale after renaming the
application</strong>: the NetworkPolicy references a label that no longer
matches anything, and the flow starts being blocked (or allowed)
silently, without anyone intentionally changing the policy.</li>
</ul>

<h3>13. Automated validation: do not rely on manual YAML review</h3>
<p>The NetworkPolicy Editor (editor.networkpolicy.io) offers a
visual interface to check the real effect of a policy before
applying it — useful precisely to catch the AND/OR mistake from section 5 before
it reaches production. Tools like <code>cnp-checker</code> and
<code>kubectl-np-viewer</code> validate rule logic
programmatically. Kyverno or Gatekeeper (covered in the Admission
Controllers lesson) can force, via admission policy, that every new
namespace is born with default-deny, closing the gap of someone forgetting the
manual step. And Hubble, beyond point debugging (section 8),
is worth running continuously in production as continuous validation that the
real network behavior still matches what the policies
declare.</p>"""
                ),
                "practical": (
                    "Em cluster com Cilium ou Calico, aplique <code>default-deny</code> em um NS "
                    "de teste, depois <code>allow-dns</code>, depois NP permitindo ingress de um "
                    "pod 'web' para um pod 'api'. Use <code>kubectl exec</code> + <code>nc -zv</code> "
                    "para validar bloqueios e permissões. Por fim, instale Hubble e veja fluxos "
                    "permitidos/negados em tempo real."
                ),
                "practical_en": (
                    "On a cluster with Cilium or Calico, apply <code>default-deny</code> in a test NS, then "
                    "<code>allow-dns</code>, then an NP allowing ingress from a 'web' pod to an 'api' pod. "
                    "Use <code>kubectl exec</code> + <code>nc -zv</code> to validate blocks and allows. "
                    "Finally, install Hubble and watch allowed/denied flows in real time."
                ),
            },
            "materials": [
                m("Kubernetes NetworkPolicy", "https://kubernetes.io/docs/concepts/services-networking/network-policies/", "docs", "", title_en="Kubernetes NetworkPolicy", description_en=""),
                m("Calico", "https://docs.tigera.io/calico/latest/about", "docs", "", title_en="Calico", description_en=""),
                m("Cilium", "https://docs.cilium.io/", "docs", "", title_en="Cilium", description_en=""),
                m("NetworkPolicy editor", "https://editor.networkpolicy.io/", "tool", "", title_en="NetworkPolicy editor", description_en=""),
                m("Cilium Cheat Sheet", "https://docs.cilium.io/en/stable/cheatsheet/", "docs", "", title_en="Cilium Cheat Sheet", description_en=""),
                m("Hubble (visualização)", "https://github.com/cilium/hubble", "tool", "", title_en="Hubble (visualization)", description_en=""),
                m("Kubernetes Network Policy Recipes", "https://github.com/ahmetb/kubernetes-network-policy-recipes", "course", "Exemplos para copiar.", title_en="Kubernetes Network Policy Recipes", description_en="Examples ready to copy."),
            ],
            "questions": [
                q("Sem NetworkPolicy:",
                  "Tráfego é totalmente permitido entre pods.",
                  ["Grande parte do o tráfego entre pods fica completamente bloqueado.", "Só o tráfego usando a porta TCP 80 é permitido.", "Só o tráfego dentro do mesmo namespace é permitido."],
                  "Pod comprometido pode atacar qualquer outro, base de muitos breaches em K8s.",
                  statement_en="Without NetworkPolicy:",
                  correct_en="Traffic is fully allowed between pods.",
                  wrong_en=["Most of the traffic between pods ends up completely blocked.", "Only traffic using TCP port 80 is allowed.", "Only traffic within the same namespace is allowed."],
                  explanation_en="A compromised pod can attack any other, the basis of many K8s breaches."),
                q("NP é avaliado no:",
                  "CNI plugin do cluster (Calico/Cilium etc.).",
                  ["Avaliado diretamente pelo processo da API server.", "Avaliado pelo controller responsável pelo Ingress.", "Avaliado pelo componente kube-proxy de cada node."],
                  "Sem CNI compatível, NP é apenas YAML decorativo.",
                  statement_en="NP is evaluated in the:",
                  correct_en="Cluster CNI plugin (Calico/Cilium etc.).",
                  wrong_en=["Evaluated directly by the API server process.", "Evaluated by the controller responsible for Ingress.", "Evaluated by the kube-proxy component on each node."],
                  explanation_en="Without a compatible CNI, NP is just decorative YAML."),
                q("Default deny ingress:",
                  "Bloqueia tráfego de entrada exceto regras explícitas.",
                  ["Substitui a necessidade de configurar RBAC no cluster.", "Aumenta bastante o uso de CPU consumido pelo node.", "Bloqueia por completo qualquer tráfego do pod."],
                  "Comece com deny-all e libere o que app realmente precisa.",
                  statement_en="Default deny ingress:",
                  correct_en="Blocks inbound traffic except for explicit rules.",
                  wrong_en=["Replaces the need to configure RBAC in the cluster.", "Greatly increases CPU usage consumed by the node.", "Completely blocks any traffic from the pod."],
                  explanation_en="Start with deny-all and open only what the app actually needs."),
                q("Selecionador por label:",
                  "Permite políticas dinâmicas conforme deploy.",
                  ["Só funciona quando o recurso é um DaemonSet.", "Seleciona os pods só pelo nome exato do recurso.", "Seleciona os pods só por um endereço IP fixo."],
                  "IPs em K8s mudam todo deploy. Labels seguem a app.",
                  statement_en="Label selector:",
                  correct_en="Enables dynamic policies as you deploy.",
                  wrong_en=["Only works when the resource is a DaemonSet.", "Selects pods only by the exact resource name.", "Selects pods only by a fixed IP address."],
                  explanation_en="IPs in K8s change on every deploy. Labels follow the app."),
                q("Cilium adiciona:",
                  "Observabilidade e Layer 7 policies via eBPF.",
                  ["Adiciona suporte só para endereçamento IPv6.", "Substitui por completo a necessidade de usar K8s.", "Adiciona só um resolvedor de DNS interno ao cluster."],
                  "Permite restringir métodos HTTP, paths, gRPC services etc.",
                  statement_en="Cilium adds:",
                  correct_en="Observability and Layer 7 policies via eBPF.",
                  wrong_en=["Adds support only for IPv6 addressing.", "Completely replaces the need to use K8s.", "Adds only an internal DNS resolver to the cluster."],
                  explanation_en="Lets you restrict HTTP methods, paths, gRPC services, and more."),
                q("NP NS-to-NS:",
                  "Selecione namespaces via namespaceSelector.",
                  ["Tecnicamente não é possível fazer esse tipo de seleção.", "Só funciona selecionando pods do mesmo namespace.", "Só funciona quando a regra já está em produção."],
                  "Use labels nos namespaces (ex.: env=prod) e selecione por elas.",
                  statement_en="NP NS-to-NS:",
                  correct_en="Select namespaces via namespaceSelector.",
                  wrong_en=["Technically it is not possible to do that kind of selection.", "Only works by selecting pods in the same namespace.", "Only works when the rule is already in production."],
                  explanation_en="Label namespaces (e.g. env=prod) and select by those labels."),
                q("Egress policy:",
                  "Limita destinos que pod pode acessar.",
                  ["Limita só conexões que usam TLS na saída.", "Limita só os headers enviados na requisição.", "Limita só a resolução de nomes DNS feita pelo pod."],
                  "Crítico para reduzir exfiltração. Combine com proxy de saída.",
                  statement_en="Egress policy:",
                  correct_en="Limits destinations the pod can reach.",
                  wrong_en=["Limits only outbound connections that use TLS.", "Limits only the headers sent in the request.", "Limits only DNS name resolution done by the pod."],
                  explanation_en="Critical to reduce exfiltration. Combine with an egress proxy."),
                q("DNS pode ser quebrado se:",
                  "Egress não permitir kube-dns explicitamente.",
                  ["Um comportamento considerado opcional na configuração.", "Um comportamento que não depende dessa configuração.", "Algo que continua funcionando bem em qualquer cenário."],
                  "Lembre-se: porta 53 UDP/TCP para kube-dns no namespace kube-system.",
                  statement_en="DNS can break if:",
                  correct_en="Egress does not explicitly allow kube-dns.",
                  wrong_en=["A behavior considered optional in the configuration.", "A behavior that does not depend on that configuration.", "Something that keeps working fine in every scenario."],
                  explanation_en="Remember: UDP/TCP port 53 to kube-dns in the kube-system namespace."),
                q("Cilium Hubble:",
                  "Observabilidade do tráfego do cluster.",
                  ["Um roteador de tráfego HTTP para o cluster.", "Um mecanismo de backup do estado do cluster.", "Um substituto direto e completo do Argo CD."],
                  "Mostra fluxos permitidos/negados em tempo real. Útil para debug de NP.",
                  statement_en="Cilium Hubble:",
                  correct_en="Observability of cluster traffic.",
                  wrong_en=["An HTTP traffic router for the cluster.", "A backup mechanism for cluster state.", "A direct and complete substitute for Argo CD."],
                  explanation_en="Shows allowed/denied flows in real time. Useful for NP debugging."),
                q("NP é:",
                  "Aditivo, múltiplas regras se acumulam.",
                  ["Substitutivo, a última regra aplicada sobrescreve as outras.", "Válido só quando aplicado no escopo global do cluster.", "Limitado a uma única política aplicada por namespace."],
                  "Cada NP soma; final é union. Ordem não importa.",
                  statement_en="NP is:",
                  correct_en="Additive; multiple rules accumulate.",
                  wrong_en=["Substitutive; the last applied rule overwrites the others.", "Valid only when applied at the global cluster scope.", "Limited to a single policy applied per namespace."],
                  explanation_en="Each NP adds; the final result is a union. Order does not matter."),
            ],
        },
        # =====================================================================
        # 5.4 Admission Controllers
        # =====================================================================
        {
            "title": "Admission Controllers",
            "title_en": "Admission Controllers",
            "summary": "Impedir que containers inseguros sejam criados.",
            "summary_en": "Stop insecure containers from being created.",
            "lesson": {
                "intro": (
                    "Toda configuração crítica começa com 'kubectl apply' bem-sucedido, e termina "
                    "com 'eu não sabia que dava pra fazer isso'. Admission controllers são a "
                    "última linha entre a intenção do usuário e a gravação no etcd. Você não "
                    "trata <em>descuido</em> com admission; você impede que descuido cause "
                    "estrago. Hoje, em prod séria, é não-negociável: PSS + Kyverno/Gatekeeper "
                    "deveria estar em todo cluster."
                ),
                "intro_en": (
                    "Every critical misconfiguration starts with a successful 'kubectl apply', and ends with "
                    "'I didn't know you could do that'. Admission controllers are the last line between the "
                    "user's intent and the write to etcd. You don't handle <em>carelessness</em> with "
                    "admission; you stop carelessness from causing damage. Today, in serious prod, it's "
                    "non-negotiable: PSS + Kyverno/Gatekeeper should be on every cluster."
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
<div class="mermaid">
flowchart LR
    Req["kubectl apply"] --> API["API server"]
    API --> Mutating["Mutating webhook"]
    Mutating --> Validating["Validating webhook"]
    Validating --> Store{"Aprovado?"}
    Store -- "Sim" --> Etcd["Persistido no etcd"]
    Store -- "Não" --> Reject["Rejeitado"]
</div>


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
                "body_en": (
                """<h3>1. The flow inside the API server: where admission enters the chain</h3>
<p>A <code>kubectl apply</code> does not write straight to etcd — it goes through a
chain of checks in a specific order, and understanding that order explains why
admission controllers exist as a category separate from RBAC.
First comes <strong>authentication</strong>: who is making this
call (certificate, OIDC, token)? Then <strong>authorization</strong>:
does that identity HAVE PERMISSION to perform this action, according to RBAC? Only
AFTER passing authentication and authorization does
<strong>mutating admission</strong> enter, which can CHANGE the request before
saving — inject an Istio sidecar, fill in a missing default.
Next comes <strong>schema validation</strong>, checking whether the YAML
is structurally correct per the CRD definition. Then
<strong>validating admission</strong> decides whether the request, already
possibly altered, PASSES the business rules — without changing
anything further, only approve or reject. Only then is the object persisted in etcd. The
practical implication: RBAC answers "can you do this?"; admission
answers "is what you are doing a good idea?" — they are two
different questions, and a user with full RBAC permission can still
be blocked by an admission policy that judges the CONTENT of the
request, not who sent it. If any admission rejects, etcd is never
touched and the user gets an error immediately.</p>
<div class="mermaid">
flowchart LR
    Req["kubectl apply"] --> API["API server"]
    API --> Mutating["Mutating webhook"]
    Mutating --> Validating["Validating webhook"]
    Validating --> Store{"Aprovado?"}
    Store -- "Sim" --> Etcd["Persistido no etcd"]
    Store -- "Não" --> Reject["Rejeitado"]
</div>


<h3>2. Three ways to implement admission</h3>
<p><strong>Built-in</strong> controllers ship compiled directly into the
apiserver — <code>NamespaceLifecycle</code>, <code>LimitRanger</code>,
<code>ResourceQuota</code>, <code>ServiceAccount</code>, and
<code>PodSecurity</code> itself (PSS, covered in the Hardening lesson) are examples.
<strong>External webhooks</strong> let YOU define the logic: the
apiserver makes an HTTPS call to a service you run, expecting an
approval or rejection response — that is the mechanism behind Kyverno and
Gatekeeper (section 3). <strong>Validating Admission Policy</strong>
(GA from Kubernetes 1.30) is a third path: policies
written in CEL (Common Expression Language), declared as a native
Kubernetes CRD, without needing any external webhook —
operationally lighter, because it removes the dependency on an
additional service answering in real time on every API call.</p>

<h3>3. The most used engines, and the trade-off between ease and power</h3>
<p><strong>Kyverno</strong> (CNCF Incubating) writes policies in pure YAML,
using the same syntax as any Kubernetes manifest — the learning
curve is the shallowest among the options, and the engine supports validate,
mutate, GENERATE new resources automatically, and even clean up old
resources. <strong>OPA Gatekeeper</strong> (CNCF Graduated, more mature)
uses Rego, Open Policy Agent's policy language — more powerful
for complex logic, but with a real learning curve, since Rego is
its own declarative language that most teams have never used
before. Gatekeeper's model separates <code>ConstraintTemplate</code>
(defines the RULE in Rego) from <code>Constraint</code> (INSTANTIATES that
rule with specific parameters) — the same rule can produce several
different constraints with distinct parameters. <strong>jsPolicy</strong>
writes policies in TypeScript, for teams that prefer a conventional
programming language to a dedicated declarative language. And
<strong>Validating Admission Policy</strong> (section 2), being native to
Kubernetes, tends to be the lowest-friction path for simpler
rules in the future, avoiding the operational dependency on an entire
external engine.</p>

<h3>4. Kyverno example: block the `:latest` tag declaratively</h3>
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
<p>The pattern <code>"!*:latest"</code> is declarative enough to
understand on first read even without knowing Kyverno — a real
advantage over the same rule written in Rego, which would require understanding the
language syntax before judging whether the logic is right.
<code>background: true</code> makes Kyverno also scan resources ALREADY
EXISTING in the cluster against that rule, not only new ones arriving
from now on — essential to discover pre-existing violations
before promoting the policy to active blocking (section 7).</p>

<h3>5. Gatekeeper example: the same idea, with Rego and CRDs</h3>
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
<p>The separation between template and constraint is what gives real reuse: the
SAME <code>ConstraintTemplate</code> for "required labels" can produce
a constraint requiring <code>[owner, team, costcenter]</code> on
Namespaces and another requiring a different set of labels on
Deployments — the Rego logic is written once, the parameters
vary per instance.</p>

<h3>6. The catalog of use cases that shows up in practically every production cluster</h3>
<p>Blocking images with the <code>latest</code> tag or from unauthorized
registries (seen in sections 4-5) is only the most common example. Requiring
<code>resources.requests/limits</code> on every pod prevents a single
unlimited workload from consuming resources uncontrollably and affecting
neighbors on the same node. Requiring mandatory labels (owner, team,
costcenter, env) is what later makes it possible to calculate cost per team
or know whom to ask when something breaks. Blocking
<code>hostPath</code>, <code>privileged</code>, and <code>runAsRoot</code>
reinforces at admission what securityContext should already guarantee
(deliberate redundancy — the admission policy catches what a
forgotten manual configuration would let through). Verifying Cosign
signatures via the sigstore policy controller (section 10) guarantees image
provenance. Auto-injecting sidecars via mutating webhook is how Istio, Linkerd,
and Vault Agent add their proxies without requiring each team to edit
every manifest by hand. Forcing a specific <code>storageClass</code>
on every PVC prevents someone accidentally using
non-replicated storage for critical data. Requiring an internal-subnet
annotation on a <code>LoadBalancer</code> Service avoids accidental
exposure to the public internet. And limiting Ingress to specific host
patterns prevents an overly generic <code>*.example.com</code> that
would end up capturing unintended traffic.</p>

<h3>7. Audit, warn, enforce: the progression that avoids mass rejection</h3>
<p>Shipping a new policy straight into blocking mode is the most
reliable way to make an entire team reject the initiative the first time
a legitimate deploy is blocked without prior warning. The correct progression
has three stages: <strong>audit</strong> only records what WOULD BE
blocked, with no visible effect for whoever is deploying —
used to discover the real impact of the rule before enabling it.
<strong>warn</strong> shows a warning in <code>kubectl apply</code> itself
but still accepts the operation, giving teams a chance to fix it on
their own before it becomes a block. <strong>enforce</strong>
finally blocks — and should only be enabled after the audit and warn
stages are already "clean" (no remaining known violations).
Jumping straight to enforce is the anti-pattern most cited in section 13.</p>

<h3>8. Webhooks in production: why an external service can take down the entire cluster</h3>
<p>A misconfigured admission webhook has unusual power: if the
apiserver depends on its response and the webhook is down, EVERY
<code>kubectl apply</code> in the cluster can hang waiting for a
response that never arrives — a single external service with the power to freeze
the entire control plane. Practical mitigations: use
<code>failurePolicy: Ignore</code> for non-critical webhooks, where a
webhook failure should not block normal operations;
<code>failurePolicy: Fail</code> only for truly security-critical ones,
but ONLY with guaranteed high availability (3+ replicas,
PodDisruptionBudget) — without that guarantee, "fail closed" becomes "cluster
stuck" on the first webhook instability. A short
<code>timeoutSeconds</code> (5 seconds or less) prevents a
slow webhook from delaying the whole cluster even while technically up.
<code>namespaceSelector</code> should explicitly exclude
<code>kube-system</code> and the webhook's own namespace — validating itself
creates a dangerous circular dependency. Having an
"emergency disable" runbook with a pre-approved script to remove the webhook
quickly is the kill switch that keeps a webhook incident from becoming a
whole-cluster outage. And monitoring the webhook's own latency and error
rate treats the admission policy as the critical infrastructure
component it actually is.</p>

<h3>9. Execution order: why mutating always runs before validating</h3>
<p>All mutating webhooks run first — there can be several at
once (the Istio injector, the Vault Agent injector, various defaults),
and the ORDER among them is not guaranteed to be deterministic. The
practical implication is to write IDEMPOTENT mutation policies —
applying the same mutation twice should produce the same result
as applying it once, since you do not control whether another mutating webhook
already altered the object before yours runs. Only after ALL mutating
webhooks finish do validating webhooks take action, and they operate
on the ALREADY MUTATED object — what goes to etcd is the
post-mutation result, not the original request sent by the user.</p>

<h3>10. Signature verification: guarantee provenance, not only content</h3>
<p>The Sigstore Policy Controller is an admission webhook specialized in
validating that an image was signed by an authorized source before
allowing it to run:</p>
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
<p>"Keyless" signing (without a manually managed key pair) uses
the CI workflow's own identity as proof — the practical effect is that
a pod only runs if the image was built and signed EXACTLY by the
authorized release workflow of that specific repository, closing
the vector of someone publishing an image with the same name from somewhere
else. Combined with SBOM and SLSA attestations (seen in Phase 4), this
forms an end-to-end verifiable supply-chain, not
just implicit trust in the registry name.</p>

<h3>11. Observability of the policies themselves: know what is being blocked, and where</h3>
<p>Kyverno automatically generates <code>PolicyReport</code> objects (CRDs)
documenting each violation found — a structured, queryable
source, instead of digging through free-text apiserver logs.
Gatekeeper exposes native Prometheus metrics: how many constraints were
violated, what the evaluation latency of each policy is. Forwarding that
to Grafana or a SIEM, and aggregating by namespace, quickly reveals
"which team accumulates the most pending violations" — a view that guides
where to invest fix effort first, instead of treating all
violations as equally urgent.</p>

<h3>12. Admission's fundamental limit: it never sees what happens afterwards</h3>
<p>Admission is entirely PREVENTIVE — it acts once, at the moment
the resource is created or updated, and never again after that. A
pod that passed every validation and was approved can still
misbehave at runtime: a compromised process trying to escalate
privilege, a binary trying to exfiltrate data, behavior
completely different from what the static configuration suggested. No
admission policy sees that, because the evaluation moment has already
passed. That is exactly the gap Falco and Tetragon (Runtime
Security lesson) fill — observing real process behavior at
runtime, not only the configuration declared at creation time.</p>

<h3>13. Five anti-patterns that sabotage adoption of admission policies</h3>
<ul>
<li><strong>Deploy straight into enforce mode</strong>: the team updates the
repository, the deploy fails without prior warning, and the natural reaction is
"turn that policy off" instead of fixing the real problem.</li>
<li><strong>Single webhook, no high availability</strong>: the entire
cluster is held hostage by a single point of failure for every admission
operation.</li>
<li><strong>Giant, ambiguous policy</strong>: hard-to-understand rules
produce confusing rejection errors, and the team learns to ignore the
message instead of fixing the cause.</li>
<li><strong>No clear remediation message</strong>: a generic "denied"
does not say HOW to fix it — including a link to the relevant runbook in
the rejection message itself saves back-and-forth.</li>
<li><strong>Policy only validates the final manifest, not the underlying Helm
chart</strong>: Helm applies the release normally, admission
rejects the result, and the release is left in a half-corrupted state —
worse than rejecting before anything is attempted.</li>
</ul>

<h3>14. Pragmatic roadmap: from install to full enforcement</h3>
<ol>
<li>Enable PSS restricted on production namespaces (Hardening
lesson) as a baseline before any custom policy.</li>
<li>Install Kyverno (lowest-friction path) or Gatekeeper, depending on the
rule complexity the team already anticipates needing.</li>
<li>Apply 5 to 10 basic policies in <em>audit</em> mode first,
never straight into enforce.</li>
<li>Share a weekly violations report with the affected
teams, giving visibility before any blocking.</li>
<li>Promote to <em>warn</em> after roughly two weeks of
audit data.</li>
<li>Promote to <em>enforce</em> only after two more weeks in
warn, with known violations already fixed.</li>
<li>Integrate image signature verification as the next layer.</li>
<li>Expand with organization-specific domain policies,
built on the already validated baseline.</li>
</ol>
"""
                ),
                "practical": (
                    "Instale Kyverno via Helm. Aplique policy bloqueando imagens com tag "
                    "<code>:latest</code> em modo <code>audit</code>. Faça <code>kubectl apply</code> "
                    "de um pod com <code>image: nginx:latest</code> e veja o <code>PolicyReport</code>. "
                    "Promova para <code>Enforce</code> e confirme que o apply é rejeitado com "
                    "mensagem clara."
                ),
                "practical_en": (
                    "Install Kyverno via Helm. Apply a policy blocking images with the <code>:latest</code> "
                    "tag in <code>audit</code> mode. Run <code>kubectl apply</code> on a pod with "
                    "<code>image: nginx:latest</code> and inspect the <code>PolicyReport</code>. Promote to "
                    "<code>Enforce</code> and confirm the apply is rejected with a clear message."
                ),
            },
            "materials": [
                m("Admission Controllers", "https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/", "docs", "", title_en="Admission Controllers", description_en=""),
                m("Gatekeeper", "https://open-policy-agent.github.io/gatekeeper/website/docs/", "docs", "", title_en="Gatekeeper", description_en=""),
                m("Kyverno policies", "https://kyverno.io/policies/", "docs", "", title_en="Kyverno policies", description_en=""),
                m("ImagePolicyWebhook", "https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#imagepolicywebhook", "docs", "", title_en="ImagePolicyWebhook", description_en=""),
                m("OPA Rego playground", "https://play.openpolicyagent.org/", "tool", "", title_en="OPA Rego playground", description_en=""),
                m("Validating Admission Policy", "https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/", "docs", "Alternativa nativa em CEL.", title_en="Validating Admission Policy", description_en="Native CEL alternative."),
                m("Sigstore Policy Controller", "https://docs.sigstore.dev/policy-controller/overview/", "docs", "Verificação de assinaturas.", title_en="Sigstore Policy Controller", description_en="Signature verification."),
            ],
            "questions": [
                q("Validating webhook:",
                  "Aprova ou rejeita pedido sem alterá-lo.",
                  ["Substitui a necessidade de configurar RBAC no cluster.", "Altera o recurso enviado antes de aprovar o pedido.", "Apaga o recurso assim que o pedido é recebido."],
                  "Mutating altera (ex.: sidecar injection); validating só decide.",
                  statement_en="Validating webhook:",
                  correct_en="Approves or rejects the request without changing it.",
                  wrong_en=["Replaces the need to configure RBAC in the cluster.", "Changes the submitted resource before approving the request.", "Deletes the resource as soon as the request is received."],
                  explanation_en="Mutating changes (e.g. sidecar injection); validating only decides."),
                q("Mutating webhook:",
                  "Modifica o recurso (ex.: injetar sidecar).",
                  ["Só cuida da resolução de nomes DNS do cluster.", "Só valida o recurso, sem alterar algum campo.", "Só gera uma linha de log sobre o recurso recebido."],
                  "Istio/Linkerd usam para injetar proxies. Vault Agent injetor também.",
                  statement_en="Mutating webhook:",
                  correct_en="Modifies the resource (e.g. inject a sidecar).",
                  wrong_en=["Only handles DNS name resolution for the cluster.", "Only validates the resource, without changing any field.", "Only writes a log line about the received resource."],
                  explanation_en="Istio/Linkerd use it to inject proxies. Vault Agent injector too."),
                q("Gatekeeper baseia-se em:",
                  "OPA com CRDs ConstraintTemplate/Constraint.",
                  ["Um arquivo YAML estático sem alguma lógica de validação.", "Um conjunto de scripts escritos em Bash.", "Um conjunto de comandos rodados direto no shell."],
                  "ConstraintTemplate define a regra Rego; Constraint instancia com parâmetros.",
                  statement_en="Gatekeeper is based on:",
                  correct_en="OPA with ConstraintTemplate/Constraint CRDs.",
                  wrong_en=["A static YAML file without any validation logic.", "A set of scripts written in Bash.", "A set of commands run directly in the shell."],
                  explanation_en="ConstraintTemplate defines the Rego rule; Constraint instantiates it with parameters."),
                q("Kyverno é:",
                  "Engine de policy nativa K8s sem precisar Rego.",
                  ["Um recurso que funciona só sobre endereçamento IPv6.", "Um substituto direto e completo do próprio kubectl.", "Uma engine que funciona só dentro de charts Helm."],
                  "Políticas em YAML usam mesma sintaxe de manifests; curva mais rasa que Rego.",
                  statement_en="Kyverno is:",
                  correct_en="A native K8s policy engine without needing Rego.",
                  wrong_en=["A resource that only works over IPv6 addressing.", "A direct and complete substitute for kubectl itself.", "An engine that only works inside Helm charts."],
                  explanation_en="YAML policies use the same manifest syntax; shallower curve than Rego."),
                q("Admission protege contra:",
                  "Recursos que violem padrões antes de existir.",
                  ["Só cobre falhas relacionadas a backup do etcd.", "Recursos que já foram criados e estão rodando no cluster.", "Só cobre a criação de recursos do tipo Service."],
                  "Pod já rodando precisa de runtime security (Falco/Tetragon).",
                  statement_en="Admission protects against:",
                  correct_en="Resources that violate standards before they exist.",
                  wrong_en=["Only covers failures related to etcd backup.", "Resources that were already created and are running in the cluster.", "Only covers creation of Service-type resources."],
                  explanation_en="A running pod needs runtime security (Falco/Tetragon)."),
                q("Modo audit:",
                  "Apenas registra violações sem bloquear.",
                  ["Bloqueia grande parte da tentativa de criação que viole a regra.", "Apaga grande parte do recurso que viole a regra configurada.", "Substitui a necessidade de manter logs do cluster."],
                  "Use para mapear; avalie achados antes de partir para enforce.",
                  statement_en="Audit mode:",
                  correct_en="Only records violations without blocking.",
                  wrong_en=["Blocks most creation attempts that violate the rule.", "Deletes most of the resource that violates the configured rule.", "Replaces the need to keep cluster logs."],
                  explanation_en="Use it to map findings; evaluate them before moving to enforce."),
                q("ImagePolicyWebhook:",
                  "Controla quais imagens podem rodar no cluster.",
                  ["Funciona só sobre endereçamento IPv6 do cluster.", "Substitui a necessidade de manter um registry próprio.", "Só cuida da resolução de nomes DNS do cluster."],
                  "Combinado com Cosign verifier, exige imagens assinadas.",
                  statement_en="ImagePolicyWebhook:",
                  correct_en="Controls which images can run in the cluster.",
                  wrong_en=["Only works over the cluster's IPv6 addressing.", "Replaces the need to maintain your own registry.", "Only handles DNS name resolution for the cluster."],
                  explanation_en="Combined with a Cosign verifier, it requires signed images."),
                q("Limite de admission:",
                  "Não enxerga problemas runtime, só no momento da admissão.",
                  ["Enxerga qualquer problema, inclusive depois do deploy, abordagem que ignora o cenário de falha mais provável na prática.", "Substitui a necessidade de ter monitoring configurado, prática que só aparece como erro grave durante um incidente real.", "Substitui a necessidade de manter logs do cluster, decisão que cria dívida técnica silenciosa, sem gerar erro imediato."],
                  "Pod aprovado pode comportar-se mal depois. Combine com runtime security.",
                  statement_en="Admission limit:",
                  correct_en="Does not see runtime problems, only at admission time.",
                  wrong_en=["Sees any problem, including after deploy, an approach that ignores the most likely failure scenario in practice.", "Replaces the need to have monitoring configured, a practice that only shows up as a serious error during a real incident.", "Replaces the need to keep cluster logs, a decision that creates silent technical debt without an immediate error."],
                  explanation_en="An approved pod can misbehave later. Combine with runtime security."),
                q("Mutating + validating:",
                  "Comum em service mesh (sidecar injection + validações).",
                  ["São exatamente o mesmo tipo de recurso do cluster.", "Os dois tipos de webhook não podem coexistir no cluster.", "Só funcionam juntos dentro de um cluster GKE."],
                  "Mutating roda primeiro, depois validating. Pode haver várias em série.",
                  statement_en="Mutating + validating:",
                  correct_en="Common in service mesh (sidecar injection + validations).",
                  wrong_en=["Are exactly the same type of cluster resource.", "The two webhook types cannot coexist in the cluster.", "Only work together inside a GKE cluster."],
                  explanation_en="Mutating runs first, then validating. Several can run in series."),
                q("Falha em webhook:",
                  "Pode bloquear o cluster inteiro, configurar failurePolicy com cuidado.",
                  ["Não tem algum efeito real sobre o cluster, suposição incorreta sobre como o sistema realmente se comporta sob estresse.", "Só gera um aviso, sem afetar o comportamento, decisão que cria dívida técnica silenciosa, sem gerar erro imediato.", "Deixa o cluster rodando mais rápido que o normal, atalho que funciona hoje mas complica a próxima migração."],
                  "failurePolicy: Fail sem high-availability = cluster down quando webhook cai.",
                  statement_en="Webhook failure:",
                  correct_en="Can block the entire cluster; configure failurePolicy carefully.",
                  wrong_en=["Has no real effect on the cluster, an incorrect assumption about how the system actually behaves under stress.", "Only generates a warning, without affecting behavior, a decision that creates silent technical debt without an immediate error.", "Makes the cluster run faster than normal, a shortcut that works today but complicates the next migration."],
                  explanation_en="failurePolicy: Fail without high availability = cluster down when the webhook dies."),
            ],
        },
        # =====================================================================
        # 5.5 Zero Trust
        # =====================================================================
        {
            "title": "Zero Trust Architecture",
            "title_en": "Zero Trust Architecture",
            "summary": "Modelo de 'nunca confiar, sempre verificar'.",
            "summary_en": "The 'never trust, always verify' model.",
            "lesson": {
                "intro": (
                    "Perímetro (firewall castelo-fosso, VPN para entrar na 'rede segura') foi "
                    "o modelo de TI corporativa por décadas. Em arquiteturas modernas, multi-"
                    "cloud, dispositivos pessoais, SaaS, trabalho remoto, microsserviços, "
                    "isso quebrou. Zero Trust assume que <strong>o atacante já está dentro</strong> "
                    "e exige autenticação/autorização contínuas em cada acesso a cada recurso. "
                    "Não é uma ferramenta; é arquitetura. Pode levar anos para amadurecer."
                ),
                "intro_en": (
                    "Perimeter (castle-and-moat firewall, VPN to enter the 'secure network') was the "
                    "corporate IT model for decades. In modern architectures, multi-cloud, personal devices, "
                    "SaaS, remote work, microservices, that broke. Zero Trust assumes that <strong>the "
                    "attacker is already inside</strong> and requires continuous authentication/authorization "
                    "on every access to every resource. It is not a tool; it is architecture. It can take "
                    "years to mature."
                ),
                "body": (
                """<h3>1. Por que o modelo de perímetro quebrou, com três incidentes que provam o ponto</h3>
<p>O modelo tradicional de TI corporativa opera em três passos simples:
o funcionário entra na VPN, passa a estar "dentro da rede corporativa", e
a partir daí acessa file servers, bancos de dados e sistemas internos
livremente. O problema estrutural é que, uma vez dentro, praticamente
TODO recurso fica alcançável — um notebook comprometido por malware dá ao
atacante o mesmo alcance que o funcionário legítimo teria; uma
credencial de ex-funcionário ainda ativa concede o mesmo acesso; um
servidor interno sem patch vira trampolim para movimento lateral sem
limite claro. Três incidentes reais ilustram exatamente essa falha
estrutural: em <strong>Target (2013)</strong>, o comprometimento de um
fornecedor de ar-condicionado — sem relação nenhuma com pagamento — deu
acesso à rede interna, de onde o atacante alcançou os sistemas de ponto
de venda e roubou 110 milhões de números de cartão. Em
<strong>OPM (2015)</strong>, um invasor permaneceu dentro da rede por
MESES sem ser detectado, exfiltrando 21 milhões de registros de
funcionários federais americanos. Em <strong>SolarWinds (2020)</strong>,
um comprometimento de supply chain fez malware rodar "dentro" de
centenas de organizações simultaneamente, cada uma confiando
implicitamente no software já instalado. Em todos os três casos, o
perímetro tecnicamente "segurou" — o firewall não foi violado por força
bruta — porque o atacante já estava do lado de dentro por outro caminho,
e uma vez lá dentro, nada mais o impedia.</p>
<div class="mermaid">
flowchart TD
    Req["Toda requisição"] --> Verify{"Identidade e contexto verificados agora?"}
    Verify -- "Sim" --> Grant["Acesso ao recurso específico"]
    Verify -- "Não" --> Deny["Acesso negado"]
</div>


<h3>2. Os cinco pilares do NIST 800-207</h3>
<p><strong>Identidade forte</strong> é a base de tudo: SSO combinado com
MFA robusto — uma chave física FIDO2 é mais forte que um código TOTP, que
por sua vez é mais forte que SMS (vulnerável a SIM swap) — porque sem
identidade verificada com confiança, nenhuma decisão de acesso posterior
tem fundamento real. <strong>Confiança no dispositivo</strong> exige que
o equipamento usado esteja gerenciado, com disco criptografado, patches
em dia, EDR (Endpoint Detection and Response) rodando e bloqueio de tela
automático — a identidade da pessoa pode estar correta, mas se o
dispositivo dela está comprometido, a credencial correta é usada por um
processo malicioso. <strong>Micro-segmentação</strong> divide a rede em
zonas pequenas, de forma que comprometer uma zona não dê alcance
automático às demais — a mesma lógica de NetworkPolicy em Kubernetes,
aplicada à rede corporativa inteira. <strong>Autorização contínua</strong>
reconhece que autenticar uma única vez, no login, não é suficiente: cada
decisão de acesso deveria ser reavaliada considerando contexto atual —
localização, nível de risco no momento, o recurso específico sendo
acessado, horário. E <strong>visibilidade</strong> — logs, traces e
correlação centralizados — é o que permite sequer DEFINIR o que é
comportamento normal, pré-requisito para detectar qualquer anomalia.</p>

<h3>3. A definição do NIST, e a palavra que muda tudo: "por requisição"</h3>
<p>O NIST SP 800-207 define Zero Trust como "uma coleção de conceitos
projetados para minimizar incerteza ao tomar decisões de acesso precisas
e de menor privilégio possível, POR REQUISIÇÃO, em sistemas e serviços
vistos como potencialmente já comprometidos". O detalhe que separa essa
definição do modelo antigo está em "por requisição", não "por sessão" —
o modelo de perímetro autentica uma vez (no login da VPN) e depois confia
indefinidamente durante toda a sessão; Zero Trust trata CADA chamada
individual como uma decisão nova, reavaliada com o contexto daquele
instante específico.</p>

<h3>4. Implementação para humanos: o modelo BeyondCorp, sem VPN</h3>
<p>O modelo popularizado pelo Google (BeyondCorp) e replicado por
ferramentas comerciais equivalentes substitui a VPN por um proxy de
decisão em cada acesso:</p>
<pre><code>Engenheiro acessa app interna em https://app.corp.example.com
→ Cloudflare Access intercepta
→ Verifica identidade (SSO + MFA)
→ Verifica device posture (laptop gerenciado? OS atualizado? EDR?)
→ Avalia policy (grupo, recurso, horário, IP)
→ Concede ou nega
→ Se OK, proxy passa request com identidade injetada (header)
→ App interno confia no header (proxy é boundary)</code></pre>
<p>O engenheiro nunca "entra numa rede" — cada acesso a cada aplicação
específica passa pela MESMA sequência de verificação, de qualquer lugar
do mundo, e o acesso concedido é escopado exatamente ao recurso
solicitado, não a uma rede inteira. A aplicação interna, por sua vez,
confia no header injetado pelo proxy — o proxy É a fronteira de
confiança, não a rede.</p>

<h3>5. Implementação serviço-a-serviço: como um pod prova identidade a outro</h3>
<p>Entre microsserviços, a pergunta muda de "quem é o humano?" para
"qual serviço específico está fazendo esta chamada, e ele deveria ter
permissão?". Um <strong>Service Mesh</strong> (Istio, Linkerd, Consul)
resolve isso automaticamente, aplicando mTLS entre cada par de serviços e
atribuindo identidade SPIFFE a cada carga de trabalho — o pod "web"
conversa com o pod "db" usando certificado mútuo, sem que o código da
aplicação precise implementar nada disso manualmente. <strong>SPIFFE/SPIRE</strong>
é o padrão aberto de identidade de carga de trabalho por trás dessa
mecânica, emitindo identidades (SVIDs) em formato X.509 ou JWT.
<strong>Workload Identity</strong> nas nuvens gerenciadas permite que
pods recebam credenciais IAM via OIDC/IMDS SEM segredo estático
armazenado em lugar nenhum — a identidade vem da própria infraestrutura,
não de um arquivo de configuração. E tokens JWT de curta duração, com
audience e issuer específicos, limitam o dano de um token eventualmente
vazado, porque ele expira rápido e só serve para o destinatário
pretendido.</p>

<h3>6. O ecossistema de ferramentas, comerciais e abertas</h3>
<p><strong>Cloudflare Access</strong> é a solução SaaS corporativa mais
conhecida para o modelo da seção 4. <strong>Tailscale</strong> constrói
uma mesh privada sobre WireGuard com identidade via SSO — uma opção
prática de Zero Trust para times pequenos e médios, sem a complexidade
de uma solução enterprise completa. <strong>Twingate, Zscaler, Netskope</strong>
e <strong>Palo Alto Prisma</strong> são soluções enterprise mais amplas.
<strong>Pomerium</strong> e <strong>Boundary</strong> (HashiCorp) são
proxies Zero Trust open-source, para quem prefere self-hosted.
<strong>Teleport</strong> centraliza acesso a SSH, Kubernetes e bancos
de dados sob uma única identidade gerenciada. E na camada de service
mesh especificamente, Istio, Linkerd e o service mesh do Cilium cobrem
a comunicação serviço-a-serviço da seção 5.</p>

<h3>7. Autorização contínua: reavaliar durante a sessão, não só no login</h3>
<p>Uma decisão única no momento do login não captura mudanças que
acontecem DEPOIS — o valor real da autorização contínua está em
reavaliar constantemente: se o IP de origem mudar drasticamente num
intervalo curto (Brasil para Romênia em 5 minutos, por exemplo, algo
fisicamente impossível para a mesma pessoa), isso sinaliza risco alto
imediato; se o dispositivo perder conformidade no meio da sessão (um
patch que deveria ter sido aplicado expirou), o acesso deveria ser
bloqueado ali mesmo, não só na próxima vez que fizer login; uma
tentativa de acessar um recurso especialmente sensível num horário
atípico pode justificar exigir MFA novamente; e um comportamento
estatisticamente incomum, como um download em volume muito acima do
padrão histórico daquele usuário, deveria disparar alerta e possivelmente
um desafio adicional (step-up authentication). Essas decisões dependem
de coleta contínua de sinal — SIEM, EDR, logs do provedor de identidade
— alimentando um motor de decisão que consegue agir em tempo real, não
só em auditoria posterior.</p>

<h3>8. O modelo de maturidade da CISA: cinco pilares, quatro estágios</h3>
<p>A CISA organiza a maturidade de Zero Trust em cinco pilares
(Identity, Devices, Networks, Applications, Data) avaliados em quatro
estágios progressivos (Traditional → Initial → Advanced → Optimal). O
valor prático desse modelo não é preencher uma planilha de conformidade
— é permitir um autodiagnóstico honesto, identificando os DOIS pilares
mais urgentes para a organização específica e definindo UMA vitória
rápida concreta por trimestre em cada um. Tentar avançar os cinco
pilares simultaneamente, de uma vez, é a receita mais comum para um
programa de Zero Trust que nunca sai do papel.</p>

<h3>9. Um padrão de adoção que funciona, e um anti-padrão que não</h3>
<p>O padrão que costuma funcionar é incremental: comece com UMA
aplicação interna nova, coloque-a atrás de um proxy de acesso (o modelo
BeyondCorp da seção 4), desligue o acesso direto antigo a ela
especificamente, e itere aplicação por aplicação a partir desse
aprendizado. O anti-padrão mais comum é o oposto: comprar um "produto
Zero Trust" tratando-o como bala de prata — um fornecedor promete "aqui
está sua arquitetura Zero Trust pronta", mas sem a mudança real de
processo, arquitetura e cultura organizacional que o modelo exige, o que
se compra é só uma camada nova de tecnologia sobre os mesmos hábitos
antigos, o equivalente a pintura nova numa casa com problema
estrutural.</p>

<h3>10. Por onde começar de verdade: um roteiro em sete passos</h3>
<ol>
<li><strong>Inventário</strong>: quais sistemas os humanos acessam
hoje, e por qual caminho — sem esse mapa, não há como priorizar nada.</li>
<li><strong>Identidade central</strong>: SSO com MFA forte para todo
mundo — o pré-requisito estrutural sem o qual nenhum dos passos
seguintes tem fundamento.</li>
<li><strong>Postura de dispositivo</strong>: uma política mínima
(criptografia, patches em dia, EDR ativo, bloqueio automático de tela)
aplicada de forma consistente.</li>
<li><strong>Acesso a aplicações internas</strong>: substituir a VPN por
um proxy de acesso para aplicações internas, começando por UMA aplicação
de baixo risco antes de expandir.</li>
<li><strong>Log centralizado</strong>: tudo enviando log para um SIEM
único, a base de qualquer detecção de anomalia futura.</li>
<li><strong>mTLS serviço-a-serviço</strong>: adotar service mesh nos
clusters Kubernetes existentes.</li>
<li><strong>Avaliação contínua</strong>: integrar sinais de risco em
tempo real às decisões de acesso, fechando o ciclo da seção 7.</li>
</ol>

<h3>11. Zero Trust dentro de um cluster Kubernetes especificamente</h3>
<p>Dentro do próprio Kubernetes, os princípios de Zero Trust já aparecem
em aulas anteriores desta fase, e juntos formam a mesma defesa em
camadas: RBAC granular (controla QUEM pode fazer O QUÊ na API);
NetworkPolicy default-deny (controla quais pods podem falar com quais);
mTLS via service mesh (prova identidade entre serviços); admission
policies (bloqueiam configuração perigosa antes de existir); audit log
centralizado num SIEM; e imagens assinadas com SBOM anexado (proveniência
verificável). Nenhuma dessas camadas sozinha implementa Zero Trust
completo — juntas, cada uma limita o raio de impacto se a anterior
falhar, exatamente o princípio de defesa em profundidade.</p>

<h3>12. Limites honestos: Zero Trust não é grátis nem universal</h3>
<p>Toda a arquitetura depende, em última análise, de identidade — se o
provedor de identidade (IdP) for comprometido, TODO o resto desmorona
junto, o que torna o hardening do próprio IdP uma prioridade crítica, não
um item qualquer na lista. Cada decisão de acesso adiciona latência real
(o proxy precisa avaliar contexto antes de liberar), um custo que
sistemas de latência ultra-sensível precisam considerar. O custo de
implementação inicial é alto, tanto em ferramenta quanto em mudança de
processo. Sistemas legados nem sempre suportam o modelo — uma aplicação
antiga que nunca foi desenhada para autenticação via header simplesmente
não tem como participar sem alguma forma de adaptação. E nem tudo
justifica o mesmo nível de rigor — uma impressora de escritório com três
anos de uso provavelmente não precisa da mesma arquitetura de Zero Trust
que o acesso ao banco de dados de produção; priorizar por risco real,
não aplicar o mesmo padrão a tudo indiscriminadamente, é o que torna o
programa sustentável.</p>"""
                ),
                "body_en": (
                """<h3>1. Why the perimeter model broke, with three incidents that prove the point</h3>
<p>The traditional corporate IT model operates in three simple steps:
the employee joins the VPN, is then "inside the corporate network", and
from there freely accesses file servers, databases, and internal systems.
The structural problem is that, once inside, practically
EVERY resource becomes reachable — a laptop compromised by malware gives the
attacker the same reach the legitimate employee would have; an
ex-employee credential still active grants the same access; an
unpatched internal server becomes a trampoline for lateral movement with no
clear limit. Three real incidents illustrate exactly that structural
failure: in <strong>Target (2013)</strong>, compromising an
HVAC vendor — with no relation to payments — gave
access to the internal network, from which the attacker reached the point-of-sale
systems and stole 110 million card numbers. In
<strong>OPM (2015)</strong>, an intruder stayed inside the network for
MONTHS undetected, exfiltrating 21 million records of
U.S. federal employees. In <strong>SolarWinds (2020)</strong>,
a supply-chain compromise made malware run "inside"
hundreds of organizations at once, each implicitly trusting
software already installed. In all three cases, the
perimeter technically "held" — the firewall was not breached by brute
force — because the attacker was already on the inside via another path,
and once there, nothing else stopped them.</p>
<div class="mermaid">
flowchart TD
    Req["Toda requisição"] --> Verify{"Identidade e contexto verificados agora?"}
    Verify -- "Sim" --> Grant["Acesso ao recurso específico"]
    Verify -- "Não" --> Deny["Acesso negado"]
</div>


<h3>2. The five pillars of NIST 800-207</h3>
<p><strong>Strong identity</strong> is the foundation of everything: SSO combined with
robust MFA — a physical FIDO2 key is stronger than a TOTP code, which
in turn is stronger than SMS (vulnerable to SIM swap) — because without
identity verified with confidence, no later access decision
has a real foundation. <strong>Device trust</strong> requires that
the equipment used is managed, with encrypted disk, patches
up to date, EDR (Endpoint Detection and Response) running, and automatic screen
lock — the person's identity may be correct, but if their
device is compromised, the correct credential is used by a
malicious process. <strong>Micro-segmentation</strong> divides the network into
small zones, so that compromising one zone does not automatically grant reach
to the others — the same NetworkPolicy logic in Kubernetes,
applied to the entire corporate network. <strong>Continuous authorization</strong>
recognizes that authenticating once, at login, is not enough: each
access decision should be re-evaluated considering current context —
location, risk level at the moment, the specific resource being
accessed, time of day. And <strong>visibility</strong> — centralized logs, traces, and
correlation — is what even lets you DEFINE what
normal behavior is, a prerequisite for detecting any anomaly.</p>

<h3>3. The NIST definition, and the word that changes everything: "per request"</h3>
<p>NIST SP 800-207 defines Zero Trust as "a collection of concepts
designed to minimize uncertainty in enforcing accurate, least privilege
per-request access decisions in information systems and services
in the face of a network viewed as compromised". The detail that separates this
definition from the old model is "per request", not "per session" —
the perimeter model authenticates once (at VPN login) and then trusts
indefinitely for the whole session; Zero Trust treats EACH individual call
as a new decision, re-evaluated with the context of that
specific instant.</p>

<h3>4. Implementation for humans: the BeyondCorp model, without VPN</h3>
<p>The model popularized by Google (BeyondCorp) and replicated by
equivalent commercial tools replaces the VPN with a decision
proxy on every access:</p>
<pre><code>Engenheiro acessa app interna em https://app.corp.example.com
→ Cloudflare Access intercepta
→ Verifica identidade (SSO + MFA)
→ Verifica device posture (laptop gerenciado? OS atualizado? EDR?)
→ Avalia policy (grupo, recurso, horário, IP)
→ Concede ou nega
→ Se OK, proxy passa request com identidade injetada (header)
→ App interno confia no header (proxy é boundary)</code></pre>
<p>The engineer never "enters a network" — each access to each specific
application goes through the SAME verification sequence, from anywhere
in the world, and the access granted is scoped exactly to the requested
resource, not to an entire network. The internal application, in turn,
trusts the header injected by the proxy — the proxy IS the trust
boundary, not the network.</p>

<h3>5. Service-to-service implementation: how one pod proves identity to another</h3>
<p>Between microservices, the question changes from "who is the human?" to
"which specific service is making this call, and should it have
permission?". A <strong>Service Mesh</strong> (Istio, Linkerd, Consul)
solves this automatically, applying mTLS between every pair of services and
assigning SPIFFE identity to each workload — the "web" pod
talks to the "db" pod using mutual certificates, without the application
code needing to implement any of that manually. <strong>SPIFFE/SPIRE</strong>
is the open workload-identity standard behind that
mechanism, issuing identities (SVIDs) in X.509 or JWT format.
<strong>Workload Identity</strong> on managed clouds lets
pods receive IAM credentials via OIDC/IMDS WITH NO static secret
stored anywhere — identity comes from the infrastructure itself,
not from a config file. And short-lived JWT tokens, with
specific audience and issuer, limit the damage of a token that eventually
leaks, because it expires quickly and only works for the intended
recipient.</p>

<h3>6. The tool ecosystem, commercial and open</h3>
<p><strong>Cloudflare Access</strong> is the best-known corporate SaaS solution
for the model in section 4. <strong>Tailscale</strong> builds
a private mesh over WireGuard with identity via SSO — a practical
Zero Trust option for small and mid-size teams, without the complexity
of a full enterprise solution. <strong>Twingate, Zscaler, Netskope</strong>
and <strong>Palo Alto Prisma</strong> are broader enterprise solutions.
<strong>Pomerium</strong> and <strong>Boundary</strong> (HashiCorp) are
open-source Zero Trust proxies, for those who prefer self-hosted.
<strong>Teleport</strong> centralizes access to SSH, Kubernetes, and databases
under a single managed identity. And specifically in the service-mesh
layer, Istio, Linkerd, and Cilium's service mesh cover
service-to-service communication from section 5.</p>

<h3>7. Continuous authorization: re-evaluate during the session, not only at login</h3>
<p>A single decision at login time does not capture changes that
happen AFTERWARDS — the real value of continuous authorization is in
constantly re-evaluating: if the source IP changes drastically in a
short interval (Brazil to Romania in 5 minutes, for example, something
physically impossible for the same person), that signals immediate high
risk; if the device loses compliance mid-session (a
patch that should have been applied expired), access should be
blocked right there, not only the next time they log in; an
attempt to access an especially sensitive resource at an atypical
time may justify requiring MFA again; and statistically
unusual behavior, such as a download volume far above that
user's historical pattern, should trigger an alert and possibly
an additional challenge (step-up authentication). These decisions depend
on continuous signal collection — SIEM, EDR, identity-provider logs
— feeding a decision engine that can act in real time, not
only in later audit.</p>

<h3>8. CISA's maturity model: five pillars, four stages</h3>
<p>CISA organizes Zero Trust maturity into five pillars
(Identity, Devices, Networks, Applications, Data) assessed across four
progressive stages (Traditional → Initial → Advanced → Optimal). The
practical value of this model is not filling a compliance spreadsheet
— it is enabling an honest self-diagnosis, identifying the TWO most
urgent pillars for the specific organization and defining ONE concrete quick
win per quarter in each. Trying to advance all five
pillars simultaneously, at once, is the most common recipe for a
Zero Trust program that never leaves the whiteboard.</p>

<h3>9. An adoption pattern that works, and an anti-pattern that does not</h3>
<p>The pattern that usually works is incremental: start with ONE
new internal application, put it behind an access proxy (the
BeyondCorp model from section 4), turn off the old direct access to it
specifically, and iterate application by application from that
learning. The most common anti-pattern is the opposite: buying a "Zero Trust
product" treating it as a silver bullet — a vendor promises "here
is your ready Zero Trust architecture", but without the real change of
process, architecture, and organizational culture the model requires, what
you buy is only a new technology layer on the same old
habits, the equivalent of fresh paint on a house with a structural
problem.</p>

<h3>10. Where to really start: a seven-step roadmap</h3>
<ol>
<li><strong>Inventory</strong>: which systems humans access
today, and by which path — without that map, there is no way to prioritize anything.</li>
<li><strong>Central identity</strong>: SSO with strong MFA for everyone
— the structural prerequisite without which none of the following
steps have a foundation.</li>
<li><strong>Device posture</strong>: a minimum policy
(encryption, patches up to date, active EDR, automatic screen lock)
applied consistently.</li>
<li><strong>Access to internal applications</strong>: replace the VPN with
an access proxy for internal applications, starting with ONE low-risk
application before expanding.</li>
<li><strong>Centralized logging</strong>: everything sending logs to a single
SIEM, the basis of any future anomaly detection.</li>
<li><strong>Service-to-service mTLS</strong>: adopt service mesh on
existing Kubernetes clusters.</li>
<li><strong>Continuous evaluation</strong>: integrate real-time risk signals into
access decisions, closing the loop from section 7.</li>
</ol>

<h3>11. Zero Trust inside a Kubernetes cluster specifically</h3>
<p>Inside Kubernetes itself, Zero Trust principles already appear
in earlier lessons in this phase, and together they form the same layered
defense: granular RBAC (controls WHO can do WHAT on the API);
default-deny NetworkPolicy (controls which pods can talk to which);
mTLS via service mesh (proves identity between services); admission
policies (block dangerous configuration before it exists); centralized audit
log in a SIEM; and signed images with attached SBOM (verifiable
provenance). None of these layers alone implements complete Zero Trust
— together, each limits the blast radius if the previous one
fails, exactly the defense-in-depth principle.</p>

<h3>12. Honest limits: Zero Trust is neither free nor universal</h3>
<p>The whole architecture ultimately depends on identity — if the
identity provider (IdP) is compromised, EVERYTHING else collapses
with it, which makes hardening the IdP itself a critical priority, not
just another item on the list. Each access decision adds real latency
(the proxy must evaluate context before allowing), a cost that
ultra-latency-sensitive systems need to consider. The cost of
initial implementation is high, both in tooling and in process
change. Legacy systems do not always support the model — an old
application never designed for header-based authentication simply
cannot participate without some form of adaptation. And not everything
justifies the same level of rigor — a three-year-old office printer
probably does not need the same Zero Trust architecture
as access to the production database; prioritizing by real risk,
not applying the same standard to everything indiscriminately, is what makes the
program sustainable.</p>
"""
                ),
                "practical": (
                    "Defina device posture mínima (disco criptografado, MFA hardware key, OS "
                    "atualizado, EDR rodando). Configure Cloudflare Access (ou Tailscale, ou "
                    "Pomerium) para que uma ferramenta interna (ex.: Grafana, ArgoCD) só seja "
                    "acessível a dispositivos que cumpram a posture. Verifique a trilha de "
                    "auditoria de quem acessou o que e quando."
                ),
                "practical_en": (
                    "Define a minimum device posture (encrypted disk, MFA hardware key, updated OS, EDR "
                    "running). Configure Cloudflare Access (or Tailscale, or Pomerium) so an internal tool "
                    "(e.g. Grafana, ArgoCD) is only reachable by devices that meet the posture. Check the "
                    "audit trail of who accessed what and when."
                ),
            },
            "materials": [
                m("NIST 800-207 Zero Trust", "https://csrc.nist.gov/publications/detail/sp/800-207/final", "docs", "", title_en="NIST 800-207 Zero Trust", description_en=""),
                m("Google BeyondCorp", "https://cloud.google.com/beyondcorp", "article", "", title_en="Google BeyondCorp", description_en=""),
                m("Cloudflare: Zero Trust", "https://www.cloudflare.com/learning/access-management/what-is-zero-trust/", "article", "", title_en="Cloudflare: Zero Trust", description_en=""),
                m("CISA Zero Trust Maturity Model", "https://www.cisa.gov/zero-trust-maturity-model", "docs", "", title_en="CISA Zero Trust Maturity Model", description_en=""),
                m("Tailscale", "https://tailscale.com/kb", "tool", "", title_en="Tailscale", description_en=""),
                m("SPIFFE/SPIRE", "https://spiffe.io/docs/latest/", "docs", "Identidade para workloads.", title_en="SPIFFE/SPIRE", description_en="Identity for workloads."),
                m("Teleport", "https://goteleport.com/docs/", "tool", "ZT acesso para SSH/K8s/DB.", title_en="Teleport", description_en="ZT access for SSH/K8s/DB."),
            ],
            "questions": [
                q("Zero Trust premissa:",
                  "Não há rede confiável, sempre autenticar/autorizar.",
                  ["Basta ter um firewall bem configurado na borda.", "A rede interna da empresa já é considerada segura.", "Uma senha forte já é o suficiente para proteger o acesso."],
                  "Assume invasor já dentro. Cada recurso = nova decisão de acesso.",
                  statement_en="Zero Trust premise:",
                  correct_en="There is no trusted network; always authenticate/authorize.",
                  wrong_en=["A well-configured edge firewall is enough.", "The company's internal network is already considered secure.", "A strong password is already enough to protect access."],
                  explanation_en="Assumes the attacker is already inside. Each resource = a new access decision."),
                q("BeyondCorp do Google é:",
                  "Implementação prática de zero trust corporativo.",
                  ["Um tipo específico de configuração de DNS interno.", "Só um mecanismo de single sign-on da empresa.", "Um cluster Kubernetes mantido internamente pelo Google."],
                  "Pioneiro: sem VPN, todo acesso via proxy + identidade + device + contexto.",
                  statement_en="Google's BeyondCorp is:",
                  correct_en="A practical implementation of corporate zero trust.",
                  wrong_en=["A specific type of internal DNS configuration.", "Just a company single sign-on mechanism.", "A Kubernetes cluster maintained internally by Google."],
                  explanation_en="Pioneer: no VPN, all access via proxy + identity + device + context."),
                q("Micro-segmentação:",
                  "Reduz blast radius, atacante não anda pela rede livremente.",
                  ["Substitui a necessidade de configurar IAM na conta, atalho comum quando o prazo aperta e ninguém revisa depois.", "Uma técnica que só faz sentido para tráfego web, suposição incorreta sobre como o sistema realmente se comporta sob estresse.", "Costuma aumentar a latência percebida pelo usuário, prática que gera falso senso de segurança no time."],
                  "Em K8s: NetworkPolicy + service mesh. Em rede: VLANs / ZTNA.",
                  statement_en="Micro-segmentation:",
                  correct_en="Reduces blast radius; the attacker cannot roam the network freely.",
                  wrong_en=["Replaces the need to configure IAM on the account, a common shortcut when the deadline is tight and nobody reviews later.", "A technique that only makes sense for web traffic, an incorrect assumption about how the system actually behaves under stress.", "Usually increases the latency perceived by the user, a practice that creates a false sense of security on the team."],
                  explanation_en="In K8s: NetworkPolicy + service mesh. On the network: VLANs / ZTNA."),
                q("Device posture:",
                  "Avalia se o dispositivo cumpre requisitos antes de acessar.",
                  ["Permite o acesso de qualquer dispositivo sem restrição.", "Avalia só o endereço IP de origem da conexão.", "Avalia só a identidade do usuário, sem olhar o dispositivo."],
                  "Disco cripto, OS atualizado, EDR rodando. Política checa no acesso.",
                  statement_en="Device posture:",
                  correct_en="Checks whether the device meets requirements before access.",
                  wrong_en=["Allows access from any device without restriction.", "Only evaluates the source IP address of the connection.", "Only evaluates the user identity, without looking at the device."],
                  explanation_en="Encrypted disk, updated OS, EDR running. Policy checks at access time."),
                q("Service mesh ajuda em:",
                  "mTLS, AuthZ, observabilidade entre serviços.",
                  ["Cuida só da resolução de nomes DNS entre serviços.", "Funciona só como uma camada de cache entre serviços.", "Substitui a necessidade de manter um ingress no cluster."],
                  "Istio/Linkerd configuram identidade por pod e cifram tráfego entre pods automaticamente.",
                  statement_en="Service mesh helps with:",
                  correct_en="mTLS, AuthZ, and observability between services.",
                  wrong_en=["Only handles DNS name resolution between services.", "Only works as a cache layer between services.", "Replaces the need to keep an ingress in the cluster."],
                  explanation_en="Istio/Linkerd set per-pod identity and encrypt traffic between pods automatically."),
                q("VPN tradicional vs Zero Trust:",
                  "VPN dá acesso amplo; ZT autoriza por recurso.",
                  ["Os dois modelos concedem exatamente o mesmo tipo de acesso.", "A VPN tradicional oferece um controle mais granular que o ZT.", "O modelo Zero Trust é considerado menos seguro que a VPN."],
                  "VPN é 'tudo ou nada'. ZT autoriza por recurso e em cada acesso.",
                  statement_en="Traditional VPN vs Zero Trust:",
                  correct_en="VPN grants broad access; ZT authorizes per resource.",
                  wrong_en=["Both models grant exactly the same type of access.", "Traditional VPN offers more granular control than ZT.", "The Zero Trust model is considered less secure than VPN."],
                  explanation_en="VPN is 'all or nothing'. ZT authorizes per resource and on every access."),
                q("Identidade forte exige:",
                  "MFA + sinal de risco contextual.",
                  ["Confiar em SMS como único fator de autenticação.", "Depender só de uma senha para autenticar o acesso.", "Depender só de um endereço IP fixo para autenticar."],
                  "FIDO2/WebAuthn é estado da arte. SMS é forma fraca (SIM swap).",
                  statement_en="Strong identity requires:",
                  correct_en="MFA + a contextual risk signal.",
                  wrong_en=["Trusting SMS as the only authentication factor.", "Relying only on a password to authenticate access.", "Relying only on a fixed IP address to authenticate."],
                  explanation_en="FIDO2/WebAuthn is state of the art. SMS is a weak form (SIM swap)."),
                q("Tailscale baseado em:",
                  "WireGuard com identidade/SSO.",
                  ["Um protocolo baseado inteiramente em L2TP.", "Um protocolo baseado inteiramente em PPTP.", "Um protocolo baseado só em IPSec, sem identidade."],
                  "Mesh privado entre dispositivos com identidade humana via OIDC. Bom ZT prático.",
                  statement_en="Tailscale is based on:",
                  correct_en="WireGuard with identity/SSO.",
                  wrong_en=["A protocol based entirely on L2TP.", "A protocol based entirely on PPTP.", "A protocol based only on IPSec, without identity."],
                  explanation_en="Private mesh between devices with human identity via OIDC. Good practical ZT."),
                q("Continuous authorization:",
                  "Reavalia decisões durante a sessão.",
                  ["Avalia a decisão só no momento do login inicial.", "Avalia a decisão só no momento do logout do usuário.", "Depende de alguém reavaliar isso manualmente."],
                  "Risco mudou (novo IP, dispositivo perdeu compliance)? Sessão é encerrada/elevada.",
                  statement_en="Continuous authorization:",
                  correct_en="Re-evaluates decisions during the session.",
                  wrong_en=["Evaluates the decision only at initial login time.", "Evaluates the decision only when the user logs out.", "Depends on someone re-evaluating it manually."],
                  explanation_en="Risk changed (new IP, device lost compliance)? Session is ended/elevated."),
                q("ZT NÃO é:",
                  "Apenas comprar uma ferramenta.",
                  ["Um conjunto de práticas apoiado por padrões do NIST.", "Um modelo que costuma ser adotado de forma gradual.", "Uma combinação de filosofia de segurança e arquitetura."],
                  "Vendors vendem 'ZT in a box'. Real ZT exige mudança de processos e arquitetura.",
                  statement_en="ZT is NOT:",
                  correct_en="Just buying a tool.",
                  wrong_en=["A set of practices backed by NIST standards.", "A model that is usually adopted gradually.", "A combination of security philosophy and architecture."],
                  explanation_en="Vendors sell 'ZT in a box'. Real ZT requires process and architecture change."),
            ],
        },
        # =====================================================================
        # 5.6 Runtime Security
        # =====================================================================
        {
            "title": "Runtime Security",
            "title_en": "Runtime Security",
            "summary": "Detectar se alguém invadiu um container em execução.",
            "summary_en": "Detect suspicious behavior while containers run.",
            "lesson": {
                "intro": (
                    "Você fez SAST, SCA, scan de imagem, hardening de pod, NetworkPolicy, "
                    "admission control, e mesmo assim algo estranho está rodando agora "
                    "naquele pod. Atacante explorou um zero-day, supply chain comprometida, "
                    "credencial vazou em log. Runtime security é a camada que detecta "
                    "atividade anômala em <em>execução</em>, 'EDR para containers'. Sem "
                    "ela, você só descobre o incidente quando o blog post sai."
                ),
                "intro_en": (
                    "You did SAST, SCA, image scan, pod hardening, NetworkPolicy, admission control, and yet "
                    "something strange is running in that pod right now. An attacker exploited a zero-day, a "
                    "compromised supply chain, a credential leaked in a log. Runtime security is the layer "
                    "that detects anomalous activity at <em>runtime</em>, 'EDR for containers'. Without it, "
                    "you only discover the incident when the blog post comes out."
                ),
                "body": (
                """<h3>1. eBPF: a tecnologia que tornou observar o kernel viável sem recompilá-lo</h3>
<p>Antes do eBPF, monitorar o comportamento real de processos exigia
módulos de kernel (LKMs) — pesados, capazes de derrubar o sistema
inteiro com um bug — ou <code>ptrace</code>, uma técnica frágil e com
overhead alto. <strong>eBPF</strong> (extended Berkeley Packet Filter)
resolve isso permitindo carregar pequenos programas, VERIFICADOS
estaticamente antes de rodar (o kernel recusa programas que possam
travar o sistema ou entrar em loop infinito), diretamente no kernel
Linux, com baixo overhead. Um programa eBPF se anexa a um syscall, a um
kprobe, a um tracepoint ou a um evento de rede, observando ou agindo sem
precisar de reboot nem patch de kernel. O que isso significa para
segurança: visibilidade granular sobre CADA syscall e CADA conexão de
rede, sem os riscos de um módulo de kernel tradicional, e sem downtime
para instalar — é a mesma tecnologia de base usada por ferramentas de
observabilidade (Pixie), de rede (Cilium) e de segurança (Falco,
Tetragon), cada uma aproveitando o mesmo mecanismo eficiente do kernel
para propósitos diferentes.</p>
<div class="mermaid">
flowchart LR
    Syscalls["Syscalls do container"] --> Falco["Monitor de runtime, ex.: Falco"]
    Falco --> Rule{"Bate com regra suspeita?"}
    Rule -- "Sim" --> Alert["Gera alerta ou ação"]
    Rule -- "Não" --> Syscalls
</div>


<h3>2. Falco: o padrão CNCF para detectar comportamento anômalo em execução</h3>
<p>Falco lê eventos do kernel via eBPF (ou, em setups mais antigos, via
módulo de kernel dedicado) e avalia cada evento contra um conjunto de
regras declaradas em YAML — rodando como DaemonSet, um por node, com
alertas saindo via stdout, syslog, ou o Falcosidekick, que roteia esses
alertas para Slack, PagerDuty ou um SIEM. As regras padrão já cobrem os
comportamentos mais reveladores de comprometimento: um shell aberto
dentro de um container de produção (via <code>kubectl exec</code>, algo
que raramente é legítimo fora de debug explícito); escrita em
<code>/etc/...</code> dentro do container, um alvo clássico de
persistência; uma conexão de saída para um IP que consta em listas de
threat intelligence; uma tentativa de escalada de privilégio via binário
setuid; leitura de arquivo sensível como <code>/etc/shadow</code> ou
<code>/proc/self/maps</code>; e "container drift" — um binário NOVO
aparecendo dentro do container que não fazia parte da imagem original,
sinal forte de que algo foi injetado depois do deploy:</p>
<pre><code># exemplo de regra Falco
- rule: Shell in container
  desc: Detecta shell em container de produção
  condition: >
    container and shell_procs and proc.tty != 0
    and not proc.pname in (allowed_shell_parent_processes)
    and k8s.ns.name in (production_ns)
  output: >
    Shell em pod prod (user=%user.name shell=%proc.name
    pod=%k8s.pod.name ns=%k8s.ns.name image=%container.image.repository)
  priority: WARNING
  tags: [container, shell, mitre_execution]</code></pre>
<p>Note a lista de exclusão (<code>allowed_shell_parent_processes</code>):
uma regra sem esse tipo de exceção geraria alerta em toda ferramenta
legítima de debug também — o equilíbrio entre sensibilidade e ruído é o
trabalho contínuo de operar Falco de verdade (seção 6).</p>

<h3>3. Tetragon: quando alertar não basta e a resposta precisa ser instantânea</h3>
<p>Tetragon (do projeto Cilium) compartilha a base eBPF com Falco, mas
tem um diferencial estrutural: consegue agir DIRETAMENTE no kernel — matar
um processo ou bloquear um syscall imediatamente, não só gerar um
alerta para um humano avaliar depois. Isso é configurado via Tracing
Policies, um CRD nativo do Kubernetes:</p>
<pre><code>apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata: { name: block-curl-in-pods }
spec:
  kprobes:
  - call: "sys_execve"
    syscall: true
    args:
    - index: 0
      type: "string"
    selectors:
    - matchArgs:
      - index: 0
        operator: "Postfix"
        values: ["/curl", "/wget"]
      matchActions:
      - action: Sigkill   # mata o processo</code></pre>
<p>Essa política mata IMEDIATAMENTE qualquer processo que tente executar
<code>curl</code> ou <code>wget</code> dentro dos pods selecionados —
útil como resposta automática a um padrão conhecido de exfiltração
(um atacante tentando baixar uma ferramenta adicional ou enviar dados
para fora). O aviso importante: ação em kernel é DEFINITIVA — ao
contrário de um alerta que um humano pode avaliar e descartar se for
falso positivo, matar um processo automaticamente pode derrubar uma
operação legítima que coincidentemente bateu no mesmo padrão, então essa
capacidade exige regras bem calibradas antes de ativar em produção.</p>

<h3>4. Outras ferramentas do mesmo espaço, cada uma com um foco distinto</h3>
<p><strong>Tracee</strong> (da Aqua) usa a mesma base eBPF com foco
específico em forense — reconstruir o que aconteceu depois do fato, não
só alertar em tempo real. <strong>Sysdig Secure</strong> é uma oferta
comercial que integra runtime security, scan de imagem e compliance numa
única plataforma. E <strong>Pixie</strong>, embora não seja uma
ferramenta de segurança primariamente, usa a mesma tecnologia eBPF para
observabilidade geral e frequentemente complementa uma stack de
segurança runtime com contexto adicional de desempenho.</p>

<h3>5. MITRE ATT&CK for Containers: um mapa para achar lacunas de cobertura</h3>
<p>A matriz específica de containers do MITRE ATT&CK organiza táticas
adversárias em categorias — Initial Access (aplicação vulnerável, imagem
maliciosa), Execution (<code>kubectl exec</code>, escape de container),
Persistence (CronJob malicioso, injeção de sidecar), Privilege Escalation
(abuso de capability, setuid), Defense Evasion (desligar logging,
esconder processo), Credential Access (ler token de ServiceAccount),
Discovery (listar pods, services, configs), Lateral Movement (explorar
um pod vizinho via API) e Impact (ransomware, mineração de
criptomoeda, exfiltração). O valor prático dessa matriz não é
decorá-la — é usá-la como CHECKLIST de cobertura: "as regras do Falco
que tenho hoje detectam T1059 (Command and Scripting Interpreter)?
T1611 (Escape to Host)? T1552 (Unsecured Credentials)?" — cada técnica
sem detecção correspondente vira candidata explícita para a próxima
regra customizada a escrever, em vez de depender de intuição sobre "o
que ainda falta cobrir".</p>

<h3>6. Operar Falco no dia a dia: da instalação ao afinamento contínuo</h3>
<p>Começar com as regras padrão é o ponto de partida certo, mas rodá-las
por duas semanas OBSERVANDO volume e qualidade dos alertas antes de
confiar cegamente nelas é o que revela onde estão os falsos positivos
específicos do seu ambiente — pods de debug com shell legítimo, escritas
esperadas em caminhos que a regra padrão não previa. Afinar essas
exceções (por label, por namespace, por processo pai esperado) é
trabalho contínuo, não uma configuração única. Regras customizadas para
o domínio específico da organização — "um pod do namespace de PCI nunca
deveria fazer egress para um IP externo", por exemplo — capturam
violações que nenhuma regra genérica do Falco antecipa. Um runbook por
nível de severidade, com SLA claro (alertas críticos respondidos em
menos de 15 minutos), transforma o alerta em ação em vez de ruído
ignorado. Integrar com SOAR (visto na aula de Incident Response) permite
resposta inicial automática — isolar o pod, tirar snapshot — antes mesmo
de um humano intervir. E rodar Game Days regularmente (aula de Security
Chaos Engineering) testando se a detecção de fato funciona é o que
diferencia "temos Falco instalado" de "sabemos que Falco detecta o que
diz que detecta".</p>

<h3>7. Respondendo a um alerta de runtime: sete passos, em ordem</h3>
<p>Diante de um alerta de alta severidade (uma tentativa de escalada de
privilégio, por exemplo), a sequência de resposta segue uma lógica
específica: primeiro <strong>confirmar</strong> — é falso positivo?
Olhar contexto, host, imagem, o evento completo antes de qualquer ação
drástica. Depois <strong>conter</strong> — aplicar uma NetworkPolicy de
<code>egress=none</code> e <code>ingress=none</code> especificamente no
pod suspeito (via seletor de label), mas SEM deletar o pod ainda, porque
apagá-lo destrói evidência forense que pode ser essencial depois. Em
seguida, <strong>forense</strong>: tirar um snapshot do filesystem do
pod (via <code>kubectl cp</code> ou um container efêmero de debug),
capturando syscalls e conexões observadas. Se necessário,
<strong>isolar o node inteiro</strong> via cordon e drain — com cuidado
para não simplesmente mover (evict) as cargas comprometidas para outro
node sem isolamento prévio, o que espalharia o problema em vez de
contê-lo. <strong>Notificar</strong> o Incident Commander e ativar o
runbook de resposta a incidente completo (aula anterior).
<strong>Erradicar</strong>: reconstruir a imagem do zero, rotacionar
credenciais, refazer deploy de tudo no namespace afetado — não só do
pod específico. E finalmente o <strong>postmortem</strong>: como o
comprometimento passou pelas camadas de prevenção anteriores? A lacuna
estava em prevenção, em detecção, ou na velocidade de resposta?</p>

<h3>8. Os limites honestos do runtime security</h3>
<p>Runtime security é fundamentalmente DETECÇÃO, não prevenção — no
momento em que Falco ou Tetragon geram um alerta, o atacante já
conseguiu executar alguma ação dentro do ambiente; a camada não impede a
entrada, só reduz o tempo até a detecção. Falsos positivos consomem
tempo real de analista de segurança, e uma ferramenta mal afinada vira
ruído que a equipe aprende a ignorar — exatamente o padrão problemático
visto em alertas mal calibrados na aula de Incident Response. Falsos
negativos também existem: um ataque suficientemente sofisticado pode ser
desenhado especificamente para evadir regras conhecidas e publicadas.
O overhead de eBPF é baixo, mas não é ZERO, especialmente em cargas de
trabalho muito intensivas em I/O, onde cada syscall observado tem um
custo marginal. E regras precisam de manutenção contínua conforme as
aplicações mudam — uma regra calibrada para o comportamento de hoje pode
gerar ruído ou, pior, deixar de detectar algo relevante amanhã. Por
esses limites, runtime security nunca substitui as camadas de PREVENÇÃO
vistas nas aulas anteriores (admission, NetworkPolicy, RBAC,
securityContext) — é uma camada adicional de defesa em profundidade,
não uma alternativa a elas.</p>

<h3>9. Escolhendo entre as opções disponíveis</h3>
<p>Entre as opções open-source e nativas de Kubernetes, Falco é a mais
madura e amplamente adotada; Tetragon se distingue pela capacidade de
ação direta em kernel (seção 3). Entre as comerciais, Sysdig Secure, Aqua
e o CrowdStrike Falcon para containers oferecem suporte e integração
mais completos, ao custo de licenciamento. E nas plataformas gerenciadas,
AWS GuardDuty for EKS e GCP Container Threat Detection observam a partir
de uma camada diferente — analisando logs do CloudTrail e de VPC, por
exemplo, em vez de syscalls diretamente no node. Essa diferença de
camada é justamente o motivo de combinar as abordagens: GuardDuty
detecta padrões visíveis na infraestrutura de nuvem ao redor do cluster;
Falco no node detecta comportamento visível de DENTRO do container — são
visões complementares, não substitutas uma da outra.</p>

<h3>10. Quatro anti-padrões que tornam a ferramenta inútil na prática</h3>
<ul>
<li><strong>Falco instalado, alertas ignorados</strong>: uma ferramenta
ruidosa sem afinamento vira spam constante, e spam constante vira
silêncio aprendido — exatamente o efeito que uma boa calibração de
regras (seção 6) deveria prevenir.</li>
<li><strong>Sem runbook de resposta</strong>: o alerta dispara
corretamente, mas ninguém sabe o próximo passo — o valor da detecção
some se a resposta não está pronta de antemão.</li>
<li><strong>Só regras padrão, nunca customizadas</strong>: o contexto
específico do próprio domínio (quais namespaces são sensíveis, quais
processos são esperados onde) exige regra própria; regra genérica
sozinha deixa lacunas conhecidas.</li>
<li><strong>Runtime security como única camada de defesa</strong>: por
ser fundamentalmente reativa (seção 8), detectar tarde demais sem as
camadas de prevenção anteriores é aceitar um nível de risco maior do que
necessário.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. eBPF: the technology that made observing the kernel viable without recompiling it</h3>
<p>Before eBPF, monitoring real process behavior required
kernel modules (LKMs) — heavy, capable of taking down the entire system
with one bug — or <code>ptrace</code>, a fragile technique with
high overhead. <strong>eBPF</strong> (extended Berkeley Packet Filter)
solves this by allowing small programs, statically VERIFIED
before running (the kernel refuses programs that could
hang the system or enter an infinite loop), to load directly into the Linux
kernel, with low overhead. An eBPF program attaches to a syscall, a
kprobe, a tracepoint, or a network event, observing or acting without
needing a reboot or kernel patch. What that means for
security: granular visibility into EVERY syscall and EVERY network
connection, without the risks of a traditional kernel module, and without downtime
to install — it is the same base technology used by observability
tools (Pixie), networking (Cilium), and security (Falco,
Tetragon), each leveraging the same efficient kernel mechanism
for different purposes.</p>
<div class="mermaid">
flowchart LR
    Syscalls["Syscalls do container"] --> Falco["Monitor de runtime, ex.: Falco"]
    Falco --> Rule{"Bate com regra suspeita?"}
    Rule -- "Sim" --> Alert["Gera alerta ou ação"]
    Rule -- "Não" --> Syscalls
</div>


<h3>2. Falco: the CNCF standard for detecting anomalous runtime behavior</h3>
<p>Falco reads kernel events via eBPF (or, in older setups, via a
dedicated kernel module) and evaluates each event against a set of
rules declared in YAML — running as a DaemonSet, one per node, with
alerts going out via stdout, syslog, or Falcosidekick, which routes those
alerts to Slack, PagerDuty, or a SIEM. Default rules already cover the
most revealing compromise behaviors: a shell opened
inside a production container (via <code>kubectl exec</code>, something
rarely legitimate outside explicit debug); writes to
<code>/etc/...</code> inside the container, a classic
persistence target; an outbound connection to an IP on threat-intelligence
lists; a privilege-escalation attempt via a setuid
binary; reading a sensitive file such as <code>/etc/shadow</code> or
<code>/proc/self/maps</code>; and "container drift" — a NEW binary
appearing inside the container that was not part of the original image,
a strong signal that something was injected after deploy:</p>
<pre><code># exemplo de regra Falco
- rule: Shell in container
  desc: Detecta shell em container de produção
  condition: >
    container and shell_procs and proc.tty != 0
    and not proc.pname in (allowed_shell_parent_processes)
    and k8s.ns.name in (production_ns)
  output: >
    Shell em pod prod (user=%user.name shell=%proc.name
    pod=%k8s.pod.name ns=%k8s.ns.name image=%container.image.repository)
  priority: WARNING
  tags: [container, shell, mitre_execution]</code></pre>
<p>Note the exclusion list (<code>allowed_shell_parent_processes</code>):
a rule without that kind of exception would also alert on every legitimate
debug tool — the balance between sensitivity and noise is the
continuous work of operating Falco for real (section 6).</p>

<h3>3. Tetragon: when alerting is not enough and the response must be instant</h3>
<p>Tetragon (from the Cilium project) shares the eBPF base with Falco, but
has a structural difference: it can act DIRECTLY in the kernel — kill
a process or block a syscall immediately, not only generate an
alert for a human to evaluate later. That is configured via Tracing
Policies, a native Kubernetes CRD:</p>
<pre><code>apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata: { name: block-curl-in-pods }
spec:
  kprobes:
  - call: "sys_execve"
    syscall: true
    args:
    - index: 0
      type: "string"
    selectors:
    - matchArgs:
      - index: 0
        operator: "Postfix"
        values: ["/curl", "/wget"]
      matchActions:
      - action: Sigkill   # mata o processo</code></pre>
<p>This policy IMMEDIATELY kills any process that tries to execute
<code>curl</code> or <code>wget</code> inside the selected pods —
useful as an automatic response to a known exfiltration pattern
(an attacker trying to download an additional tool or send data
out). The important warning: kernel action is DEFINITIVE — unlike
an alert a human can evaluate and discard if it is a
false positive, automatically killing a process can take down a
legitimate operation that coincidentally matched the same pattern, so that
capability requires well-calibrated rules before enabling in production.</p>

<h3>4. Other tools in the same space, each with a distinct focus</h3>
<p><strong>Tracee</strong> (from Aqua) uses the same eBPF base with a specific
focus on forensics — reconstructing what happened after the fact, not
only alerting in real time. <strong>Sysdig Secure</strong> is a commercial
offering that integrates runtime security, image scanning, and compliance in a
single platform. And <strong>Pixie</strong>, although not primarily a
security tool, uses the same eBPF technology for
general observability and often complements a runtime security
stack with additional performance context.</p>

<h3>5. MITRE ATT&CK for Containers: a map to find coverage gaps</h3>
<p>MITRE ATT&CK's container-specific matrix organizes adversary
tactics into categories — Initial Access (vulnerable application, malicious
image), Execution (<code>kubectl exec</code>, container escape),
Persistence (malicious CronJob, sidecar injection), Privilege Escalation
(capability abuse, setuid), Defense Evasion (disable logging,
hide process), Credential Access (read ServiceAccount token),
Discovery (list pods, services, configs), Lateral Movement (explore
a neighboring pod via the API), and Impact (ransomware, cryptocurrency
mining, exfiltration). The practical value of this matrix is not
memorizing it — it is using it as a coverage CHECKLIST: "do the Falco rules
I have today detect T1059 (Command and Scripting Interpreter)?
T1611 (Escape to Host)? T1552 (Unsecured Credentials)?" — each technique
without matching detection becomes an explicit candidate for the next
custom rule to write, instead of relying on intuition about "what
is still missing".</p>

<h3>6. Operating Falco day to day: from install to continuous tuning</h3>
<p>Starting with the default rules is the right starting point, but running them
for two weeks OBSERVING alert volume and quality before
trusting them blindly is what reveals where the environment-specific false
positives are — debug pods with a legitimate shell, expected writes
to paths the default rule did not anticipate. Tuning those
exceptions (by label, by namespace, by expected parent process) is
continuous work, not a one-time configuration. Custom rules for the
organization's specific domain — "a pod in the PCI namespace should never
egress to an external IP", for example — catch
violations no generic Falco rule anticipates. A runbook per
severity level, with a clear SLA (critical alerts answered in
under 15 minutes), turns the alert into action instead of ignored
noise. Integrating with SOAR (covered in the Incident Response lesson) enables
automatic initial response — isolate the pod, take a snapshot — even before
a human intervenes. And running Game Days regularly (Security
Chaos Engineering lesson) testing whether detection actually works is what
differentiates "we have Falco installed" from "we know Falco detects what
it says it detects".</p>

<h3>7. Responding to a runtime alert: seven steps, in order</h3>
<p>Faced with a high-severity alert (a privilege-escalation
attempt, for example), the response sequence follows a specific
logic: first <strong>confirm</strong> — is it a false positive?
Look at context, host, image, the full event before any drastic
action. Then <strong>contain</strong> — apply a NetworkPolicy of
<code>egress=none</code> and <code>ingress=none</code> specifically on the
suspect pod (via label selector), but WITHOUT deleting the pod yet, because
deleting it destroys forensic evidence that may be essential later. Next,
<strong>forensics</strong>: take a snapshot of the pod's filesystem
(via <code>kubectl cp</code> or an ephemeral debug container),
capturing observed syscalls and connections. If needed,
<strong>isolate the entire node</strong> via cordon and drain — carefully
so as not to simply move (evict) compromised workloads to another
node without prior isolation, which would spread the problem instead of
containing it. <strong>Notify</strong> the Incident Commander and activate the
full incident-response runbook (previous lesson).
<strong>Eradicate</strong>: rebuild the image from scratch, rotate
credentials, redeploy everything in the affected namespace — not only the
specific pod. And finally the <strong>postmortem</strong>: how did the
compromise get past the earlier prevention layers? Was the gap
in prevention, in detection, or in response speed?</p>

<h3>8. Honest limits of runtime security</h3>
<p>Runtime security is fundamentally DETECTION, not prevention — by the
moment Falco or Tetragon generate an alert, the attacker has already
managed to execute some action inside the environment; the layer does not prevent
entry, it only reduces time to detection. False positives consume
real security-analyst time, and a poorly tuned tool becomes
noise the team learns to ignore — exactly the problematic pattern
seen with poorly calibrated alerts in the Incident Response lesson. False
negatives also exist: a sufficiently sophisticated attack can be
designed specifically to evade known, published rules.
eBPF overhead is low, but it is not ZERO, especially on very
I/O-intensive workloads, where each observed syscall has a
marginal cost. And rules need continuous maintenance as
applications change — a rule calibrated for today's behavior may
generate noise or, worse, stop detecting something relevant tomorrow. Because of
these limits, runtime security never replaces the PREVENTION layers
seen in earlier lessons (admission, NetworkPolicy, RBAC,
securityContext) — it is an additional defense-in-depth layer,
not an alternative to them.</p>

<h3>9. Choosing among the available options</h3>
<p>Among open-source and Kubernetes-native options, Falco is the most
mature and widely adopted; Tetragon stands out for its ability to
act directly in the kernel (section 3). Among commercial offerings, Sysdig Secure, Aqua,
and CrowdStrike Falcon for containers offer more complete support and
integration, at the cost of licensing. And on managed platforms,
AWS GuardDuty for EKS and GCP Container Threat Detection observe from
a different layer — analyzing CloudTrail and VPC logs, for
example, instead of syscalls directly on the node. That layer
difference is exactly why you combine the approaches: GuardDuty
detects patterns visible in the cloud infrastructure around the cluster;
Falco on the node detects behavior visible FROM INSIDE the container — they are
complementary views, not substitutes for each other.</p>

<h3>10. Four anti-patterns that make the tool useless in practice</h3>
<ul>
<li><strong>Falco installed, alerts ignored</strong>: a noisy tool
without tuning becomes constant spam, and constant spam becomes
learned silence — exactly the effect good rule calibration
(section 6) should prevent.</li>
<li><strong>No response runbook</strong>: the alert fires
correctly, but nobody knows the next step — the value of detection
vanishes if the response is not ready beforehand.</li>
<li><strong>Only default rules, never customized</strong>: the organization's
specific domain context (which namespaces are sensitive, which
processes are expected where) requires its own rules; generic rules
alone leave known gaps.</li>
<li><strong>Runtime security as the only defense layer</strong>: because it
is fundamentally reactive (section 8), detecting too late without the
earlier prevention layers is accepting a higher risk level than
necessary.</li>
</ul>
"""
                ),
                "practical": (
                    "Instale Falco via Helm. Faça <code>kubectl exec -it &lt;pod&gt; -- bash</code> "
                    "em um pod e veja o alerta 'Terminal shell in container' nos logs do Falco. "
                    "Tune a regra para ignorar pods com label <code>debug=true</code> mas mantenha "
                    "alerta para pods sem essa label. Em seguida, configure Falcosidekick para "
                    "enviar alertas para um webhook simples (httpbin.org) e simule um evento "
                    "high-severity."
                ),
                "practical_en": (
                    "Install Falco via Helm. Run <code>kubectl exec -it &lt;pod&gt; -- bash</code> in a pod "
                    "and see the 'Terminal shell in container' alert in Falco logs. Tune the rule to ignore "
                    "pods with label <code>debug=true</code> but keep the alert for pods without that label. "
                    "Then configure Falcosidekick to send alerts to a simple webhook (httpbin.org) and "
                    "simulate a high-severity event."
                ),
            },
            "materials": [
                m("Falco", "https://falco.org/docs/", "docs", "", title_en="Falco", description_en=""),
                m("Tetragon", "https://tetragon.io/docs/", "docs", "", title_en="Tetragon", description_en=""),
                m("Sysdig: Container security", "https://sysdig.com/learn-cloud-native/", "article", "", title_en="Sysdig: Container security", description_en=""),
                m("eBPF.io", "https://ebpf.io/", "docs", "", title_en="eBPF.io", description_en=""),
                m("MITRE ATT&CK Containers", "https://attack.mitre.org/matrices/enterprise/containers/", "docs", "", title_en="MITRE ATT&CK Containers", description_en=""),
                m("Falcosidekick", "https://github.com/falcosecurity/falcosidekick", "tool", "Roteia alertas Falco.", title_en="Falcosidekick", description_en="Routes Falco alerts."),
                m("Tracee", "https://aquasecurity.github.io/tracee/latest/", "tool", "Forensics + runtime.", title_en="Tracee", description_en="Forensics + runtime."),
            ],
            "questions": [
                q("Falco detecta:",
                  "Comportamentos suspeitos via syscalls/eBPF.",
                  ["Vulnerabilidades encontradas por uma análise estática do código.", "Só cuida da resolução de nomes DNS do cluster.", "Só analisa pacotes usando o protocolo ICMP."],
                  "Como antivírus comportamental para containers. Detecta ações, não assinaturas estáticas.",
                  statement_en="Falco detects:",
                  correct_en="Suspicious behaviors via syscalls/eBPF.",
                  wrong_en=["Vulnerabilities found by static analysis of the code.", "Only handles DNS name resolution for the cluster.", "Only analyzes packets using the ICMP protocol."],
                  explanation_en="Like behavioral antivirus for containers. Detects actions, not static signatures."),
                q("eBPF permite:",
                  "Programas seguros no kernel sem modificar fonte.",
                  ["Um recurso que só está disponível rodando em macOS.", "Exige recompilar o kernel inteiro para funcionar.", "Só funciona quando o processo roda como usuário root."],
                  "Verificador estático garante que o programa não trava o kernel. Revolução em observability.",
                  statement_en="eBPF allows:",
                  correct_en="Safe programs in the kernel without changing the source.",
                  wrong_en=["A feature that is only available when running on macOS.", "Requires recompiling the entire kernel to work.", "Only works when the process runs as the root user."],
                  explanation_en="A static verifier guarantees the program will not crash the kernel. A revolution in observability."),
                q("Detecção runtime complementa:",
                  "Controles preventivos (SAST, SCA, admission).",
                  ["Reduz a necessidade de manter IAM configurado.", "Substitui por completo vários outros controles existentes.", "Substitui a necessidade de manter logs do cluster."],
                  "Defesa em camadas: prevenir + detectar + responder.",
                  statement_en="Runtime detection complements:",
                  correct_en="Preventive controls (SAST, SCA, admission).",
                  wrong_en=["Reduces the need to keep IAM configured.", "Completely replaces several other existing controls.", "Replaces the need to keep cluster logs."],
                  explanation_en="Defense in depth: prevent + detect + respond."),
                q("Shell em pod produção é:",
                  "Sinal a investigar, geralmente anomalia.",
                  ["Uma prática considerada necessária no dia a dia.", "Uma prática recomendada pela maioria dos guias de operação.", "Uma situação comum e esperada em ambiente de produção."],
                  "Em prod imutável, kubectl exec é exceção. Auditoria mostra quem e quando.",
                  statement_en="A shell in a production pod is:",
                  correct_en="A signal to investigate, usually an anomaly.",
                  wrong_en=["A practice considered necessary day to day.", "A practice recommended by most operations guides.", "A common and expected situation in a production environment."],
                  explanation_en="In immutable prod, kubectl exec is the exception. Audit shows who and when."),
                q("Tetragon difere de Falco:",
                  "Tetragon tem ações ativas (kill) em kernel.",
                  ["Uma ferramenta que não permite configurar alguma regra.", "Duas ferramentas praticamente idênticas em funcionalidade.", "O Falco é escrito inteiramente na linguagem Java."],
                  "Falco alerta; Tetragon pode bloquear/kill imediatamente.",
                  statement_en="Tetragon differs from Falco:",
                  correct_en="Tetragon has active actions (kill) in the kernel.",
                  wrong_en=["A tool that does not allow configuring any rule.", "Two tools that are practically identical in functionality.", "Falco is written entirely in the Java language."],
                  explanation_en="Falco alerts; Tetragon can block/kill immediately."),
                q("MITRE ATT&CK:",
                  "Knowledge base de táticas/técnicas de adversários.",
                  ["Um ambiente de desenvolvimento integrado (IDE).", "Um compilador usado para gerar binários otimizados.", "Um tipo específico de cluster Kubernetes gerenciado."],
                  "Use para mapear regras Falco/Tetragon e medir cobertura defensiva.",
                  statement_en="MITRE ATT&CK:",
                  correct_en="A knowledge base of adversary tactics/techniques.",
                  wrong_en=["An integrated development environment (IDE).", "A compiler used to generate optimized binaries.", "A specific type of managed Kubernetes cluster."],
                  explanation_en="Use it to map Falco/Tetragon rules and measure defensive coverage."),
                q("Sidecar de monitoramento:",
                  "Pode aumentar overhead, escolha modo eBPF/host quando possível.",
                  ["Um componente que só funciona rodando como DaemonSet, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas.", "Um componente que praticamente não gera overhead algum, que só aparece como problema depois que o sistema já está em produção.", "Um componente considerado obrigatório em qualquer cluster, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "DaemonSet com eBPF tem footprint menor que sidecar por pod.",
                  statement_en="Monitoring sidecar:",
                  correct_en="Can increase overhead; prefer eBPF/host mode when possible.",
                  wrong_en=["A component that only works running as a DaemonSet, a shortcut that looks safe in isolation but breaks when combined with other systems.", "A component that generates practically no overhead at all, which only shows up as a problem after the system is already in production.", "A component considered mandatory on any cluster, an assumption that only holds in a development environment, not in production."],
                  explanation_en="A DaemonSet with eBPF has a smaller footprint than a sidecar per pod."),
                q("Falsos positivos:",
                  "Devem ser tunados via regras customizadas.",
                  ["Devem ser ignorados na grande maioria dos casos.", "Devem levar à desativação completa da ferramenta.", "Devem ser resolvidos trocando de ferramenta de detecção."],
                  "Cada ambiente tem padrões diferentes. Tuning é trabalho contínuo.",
                  statement_en="False positives:",
                  correct_en="Should be tuned via customized rules.",
                  wrong_en=["Should be ignored in the vast majority of cases.", "Should lead to completely disabling the tool.", "Should be solved by switching detection tools."],
                  explanation_en="Each environment has different patterns. Tuning is continuous work."),
                q("Resposta a alerta runtime:",
                  "Runbook claro com escala e isolamento.",
                  ["Apagar os logs relacionados ao alerta recebido.", "Ignorar o alerta até que ele pare de aparecer.", "Reiniciar vários serviços do cluster de uma vez."],
                  "Snapshot do pod (forensics), isolar (NP), notificar IR. Não delete sem evidência.",
                  statement_en="Response to a runtime alert:",
                  correct_en="A clear runbook with escalation and isolation.",
                  wrong_en=["Deleting the logs related to the received alert.", "Ignoring the alert until it stops appearing.", "Restarting several cluster services at once."],
                  explanation_en="Snapshot the pod (forensics), isolate (NP), notify IR. Don't delete without evidence."),
                q("Observabilidade runtime:",
                  "Dá visão 'em vivo' do que cluster faz.",
                  ["Substitui a necessidade de coletar métricas do cluster.", "Serve só para depuração manual feita por um dev.", "Praticamente não funciona bem em ambiente de produção."],
                  "Hubble/Pixie mostram execuções/conexões em tempo real, útil em incidente.",
                  statement_en="Runtime observability:",
                  correct_en="Gives a live view of what the cluster is doing.",
                  wrong_en=["Replaces the need to collect cluster metrics.", "Only serves manual debugging done by a developer.", "Practically does not work well in a production environment."],
                  explanation_en="Hubble/Pixie show executions/connections in real time, useful in an incident."),
            ],
        },
        # =====================================================================
        # 5.7 Observabilidade Avançada
        # =====================================================================
        {
            "title": "Observabilidade Avançada",
            "title_en": "Advanced Observability",
            "summary": "Rastrear o caminho de uma requisição entre sistemas.",
            "summary_en": "Trace a request's path across systems.",
            "lesson": {
                "intro": (
                    "Métricas dizem 'o quê' (CPU 80%, latência p99 1s); logs dizem 'o que "
                    "aconteceu' (exception em handler); traces dizem 'por onde foi' (login → "
                    "auth → DB → cache → email). Em arquitetura distribuída com 30+ "
                    "microsserviços, sem traces você investiga incidentes às cegas. "
                    "Observabilidade avançada é dominar os três pilares, e correlacioná-los."
                ),
                "intro_en": (
                    "Metrics say 'what' (CPU 80%, p99 latency 1s); logs say 'what happened' (exception in a "
                    "handler); traces say 'where it went' (login → auth → DB → cache → email). In a "
                    "distributed architecture with 30+ microservices, without traces you investigate "
                    "incidents blind. Advanced observability is mastering the three pillars, and correlating "
                    "them."
                ),
                "body": (
                """<h3>1. Os três pilares: por que nenhum sozinho basta para investigar um incidente</h3>
<p><strong>Métricas</strong> são séries temporais de números agregados —
"requisições/segundo", "erro 500/segundo", "CPU%" — baratas de armazenar
e estatisticamente poderosas, mas com cardinalidade baixa por
necessidade: elas dizem O QUÊ está acontecendo em agregado, sem detalhe
de nenhuma requisição específica. <strong>Logs</strong> são eventos
textuais discretos ("login failed for user@x"), com detalhe muito maior
que uma métrica pode carregar, mas com custo de armazenamento
proporcionalmente maior e busca por texto livre, não por agregação
numérica. <strong>Traces</strong> são a árvore de spans que representa o
CAMINHO real de uma requisição através de vários serviços — a única das
três fontes que responde "por onde essa chamada específica passou, e
onde o tempo foi gasto". Cada pilar responde uma pergunta diferente;
numa arquitetura com dezenas de microsserviços, investigar um incidente
usando só um dos três é like tentar reconstruir um crime vendo só a foto,
só o áudio, ou só o vídeo — os três JUNTOS, correlacionados (seção 8), é
o que permite raciocínio rápido durante um incidente real.</p>
<div class="mermaid">
flowchart LR
    subgraph Pilares ["Três pilares"]
        Logs["Logs"]
        Metrics["Métricas"]
        Traces["Traces"]
    end
    Logs --> Correl["Correlacionados por trace_id"]
    Metrics --> Correl
    Traces --> Correl
</div>


<h3>2. Tracing: uma requisição vira árvore, não uma linha de log</h3>
<p>Uma requisição inteira é um <strong>trace</strong>; cada operação
dentro dela (uma chamada de autenticação, uma query de banco, uma
chamada a outro serviço) é um <strong>span</strong>, e os spans formam
uma árvore com relação explícita de pai e filho:</p>
<pre><code>POST /checkout                              [800ms]
├── auth.verify_token                       [10ms]
├── inventory.check_stock                   [30ms]
├── payment.charge                          [600ms]
│   ├── stripe.create_charge                [580ms]
│   └── db.write_charge                     [15ms]
├── notification.send_email                 [40ms]
└── db.write_order                          [20ms]</code></pre>
<p>Só de olhar essa árvore, fica óbvio ONDE os 800ms totais foram gastos:
<code>payment.charge</code> consome 600ms, e dentro dele a chamada
externa ao Stripe (580ms) domina — informação que uma métrica de
"latência média do checkout" jamais revelaria sozinha. Cada span carrega
um <code>trace_id</code> (identifica o trace inteiro), um
<code>span_id</code> (identifica esse span específico), um
<code>parent_span_id</code> (de onde ele veio), timestamps de início e
fim, nome do serviço e da operação, status (ok/erro), atributos
(<code>http.method</code>, <code>db.statement</code>, <code>user.id</code>)
e eventos (logs locais ao próprio span). A propagação entre serviços
segue o padrão W3C TraceContext, carregado em headers HTTP comuns:</p>
<pre><code>traceparent: 00-{trace-id-32-hex}-{parent-id-16-hex}-{flags-2-hex}
tracestate: rojo=00f067aa0ba902b7</code></pre>
<p>É esse header propagado de serviço a serviço que permite reconstruir
a árvore inteira depois — sem ele, cada serviço só saberia da própria
parte, sem noção de que fazem parte da mesma requisição original.</p>

<h3>3. OpenTelemetry: um padrão para não reescrever instrumentação a cada troca de backend</h3>
<p>OpenTelemetry (OTel, projeto CNCF) resolve um problema real: antes
dele, instrumentar código para um backend específico de tracing
significava reescrever essa instrumentação inteira se a empresa
decidisse trocar de fornecedor. O SDK, disponível em cada linguagem,
instrumenta o código; a auto-instrumentação cobre bibliotecas comuns
(HTTP, banco de dados, RPC) SEM exigir mudança manual de código; o OTLP é
o protocolo binário (gRPC ou HTTP) que carrega os dados entre a aplicação
e o coletor; e o Collector é um agente que recebe dados em múltiplos
formatos (OTLP, Jaeger, Zipkin, Prometheus), processa, e exporta para
QUALQUER backend escolhido — trocar de Jaeger para Tempo, por exemplo,
vira uma mudança de configuração do coletor, não uma reescrita de
instrumentação em cada serviço:</p>
<pre><code># Python
$ pip install opentelemetry-distro opentelemetry-exporter-otlp
$ opentelemetry-bootstrap --action=install
$ OTEL_SERVICE_NAME=checkout \\
  OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \\
  opentelemetry-instrument python app.py
# pronto: traces para HTTP, requests, sqlalchemy, redis... aparecem no backend</code></pre>

<h3>4. Backends de trace: cada um resolve um trade-off diferente de custo e poder</h3>
<p><strong>Jaeger</strong> é o backend CNCF clássico, usando Cassandra
ou Elasticsearch como armazenamento — maduro, mas o custo de storage
cresce junto com o volume de traces. <strong>Tempo</strong> (Grafana)
usa armazenamento baseado em S3/GCS, dramaticamente mais barato para
grandes volumes, ao custo de queries um pouco menos ricas que soluções
com índice dedicado. <strong>Zipkin</strong> foi pioneiro (originado no
Twitter) e ainda é usado em sistemas legados. <strong>Honeycomb</strong>
é SaaS especializado em ALTA cardinalidade — permite queries
interativas explorando combinações de atributos que backends
tradicionais não suportariam bem. <strong>Datadog APM</strong>, New
Relic e Dynatrace são plataformas SaaS comerciais completas, cobrindo os
três pilares numa única assinatura. <strong>SigNoz</strong> e
<strong>Uptrace</strong> são alternativas open-source self-hosted para
quem quer o controle sem o custo recorrente de SaaS.</p>

<h3>5. Métricas: por que média esconde exatamente o problema que você precisa ver</h3>
<p>Trabalhar com histogramas em vez de médias é a diferença entre saber
que existe um problema e saber quão grave ele é para uma fração real de
usuários:</p>
<pre><code>avg_latency = 100ms                    # parece bom
p50 = 50ms
p99 = 5s                                # 1% dos usuários: experiência terrível</code></pre>
<p>Uma média de 100ms parece perfeitamente saudável — mas o p99 de 5
segundos revela que 1% dos usuários (que pode ser um número absoluto
grande, dependendo do tráfego) tem uma experiência terrível que a média
sozinha esconde completamente. Três estruturas mentais complementares
ajudam a decidir O QUE medir: RED (de Tom Wilkie), focado em SERVIÇOS —
Rate (requisições/segundo), Errors (erros/segundo), Duration (distribuição
de latência); USE (de Brendan Gregg), focado em RECURSOS — Utilization
(percentual de uso), Saturation (fila de espera acumulada), Errors
(erros do próprio recurso); e os Quatro Sinais Dourados do Google SRE —
latency, traffic, errors, saturation, essencialmente uma síntese das
duas anteriores adaptada para qualquer serviço.</p>

<h3>6. Cardinalidade: a armadilha que derruba um Prometheus mal configurado</h3>
<p>Cardinalidade é o número de séries TEMPORAIS ÚNICAS que uma métrica
gera — cada combinação distinta de valores de label cria uma série nova
e separada para o banco de séries temporais armazenar:</p>
<pre><code># RUIM
http_requests_total{user_id="123", path="/api/users/456"}
# 1M users * 100k paths = 100B séries → quebra Prometheus

# BOM
http_requests_total{route="/api/users/:id", method="GET", status="200"}
# poucas séries, alta utilidade</code></pre>
<p>Usar <code>user_id</code> ou o path COMPLETO (com ID específico) como
label parece inofensivo linha a linha, mas multiplica combinações de
forma explosiva — um milhão de usuários vezes cem mil paths diferentes
gera cardinalidade que nenhum Prometheus, Cortex ou Mimir aguenta
operacionalmente. A rota PARAMETRIZADA (<code>/api/users/:id</code> em
vez do ID literal) mantém a cardinalidade baixa e ainda entrega a
informação agregada útil. Detalhe de alto-cardinalidade — QUAL usuário
específico, QUAL requisição específica — pertence a traces e logs, que
são projetados desde a concepção para lidar com esse volume de forma
diferente de uma série temporal.</p>

<h3>7. Sampling: coletar tudo custa caro, coletar amostra errada esconde o que importa</h3>
<p>Capturar 100% dos traces produzidos por um sistema de alto tráfego
tem custo de armazenamento proibitivo na maioria dos casos — por isso
existem estratégias de amostragem, cada uma com um trade-off distinto.
<strong>Head-based</strong> decide na PRIMEIRA chamada, aleatoriamente
(por exemplo, guardar N% de tudo) — simples de implementar, mas tende a
perder justamente os casos raros e interessantes (o erro ocasional, a
requisição excepcionalmente lenta), porque a decisão é tomada ANTES de
saber se aquele trace seria interessante. <strong>Tail-based</strong>
inverte a lógica: coleta tudo temporariamente, e só decide DEPOIS,
olhando o trace completo — permitindo priorizar deliberadamente erros e
requisições lentas, exatamente os casos que head-based tende a perder.
O custo é operacional: exige um coletor com buffer, guardando traces
temporariamente até a decisão ser tomada. <strong>Probabilístico</strong>
é uma amostra fixa simples (por exemplo, sempre 1%). E
<strong>rate-limiting</strong> impõe um teto absoluto de traces por
segundo, por serviço, independente do volume total de tráfego:</p>
<pre><code># OTel Collector tail sampling
processors:
  tail_sampling:
    decision_wait: 30s
    policies:
    - name: errors-policy
      type: status_code
      status_code: { status_codes: [ERROR] }
    - name: slow-policy
      type: latency
      latency: { threshold_ms: 1000 }
    - name: random-policy
      type: probabilistic
      probabilistic: { sampling_percentage: 1 }</code></pre>
<p>Essa configuração combina as três estratégias: sempre guarda erros,
sempre guarda o que é lento, e amostra 1% do resto — o padrão mais comum
em produção, porque preserva exatamente os casos que mais importam para
debug sem pagar o custo de guardar tudo.</p>

<h3>8. Correlação: o que transforma três fontes separadas numa investigação rápida</h3>
<p>Incluir o <code>trace_id</code> em CADA linha de log é o elo que
conecta as três fontes de observabilidade:</p>
<pre><code>{"timestamp": "...", "level": "ERROR",
 "service": "payment", "trace_id": "4bf92f3577b34da6",
 "span_id": "00f067aa0ba902b7",
 "msg": "stripe charge failed", "user_id": "u-123"}</code></pre>
<p>Com essa correlação e uma stack como Grafana com Loki (logs) + Tempo
(traces) + Prometheus (métricas), o fluxo de investigação de um
incidente vira literalmente clicável: você vê o pico de erro numa
métrica; faz drill-down nos logs daquele serviço no mesmo intervalo de
tempo; clica no <code>trace_id</code> de um log de erro específico e cai
DIRETO no trace correspondente; e no trace, vê exatamente qual span
falhou e quanto tempo cada etapa consumiu. Sem essa correlação, a mesma
investigação exigiria correlacionar manualmente timestamps entre três
sistemas diferentes — inviável na velocidade que um incidente real
exige.</p>

<h3>9. SLI, SLO e Error Budget: transformar "está funcionando bem?" numa pergunta numérica</h3>
<p>Um <strong>SLI</strong> (Service Level Indicator) é uma métrica que
mede a experiência real do usuário — "percentual de requisições abaixo
de 500ms", por exemplo. Um <strong>SLO</strong> (Objective) é uma META
numérica sobre esse indicador — "99,9% das requisições abaixo de 500ms
numa janela de 30 dias". O <strong>Error Budget</strong> é o
complemento aritmético do SLO: 100% menos 99,9% deixa 0,1% de margem
para erro, que para uma janela de 30 dias equivale a cerca de 43 minutos
de indisponibilidade TOLERADA por mês — e quando esse orçamento está
sendo consumido rápido demais, a resposta operacional correta é
CONGELAR novos deploys até a situação estabilizar, não continuar
lançando mudanças que aumentam o risco. Um <strong>SLA</strong> é o
compromisso CONTRATUAL com o cliente, tipicamente definido mais frouxo
que o SLO interno de propósito — a folga entre os dois é o que permite à
equipe detectar e corrigir um problema ANTES que ele viole o contrato
formal com o cliente.</p>

<h3>10. Alerting eficaz: o alerta que não gera ação é ruído, não sinal</h3>
<p>Um alerta só se justifica quando é <strong>acionável</strong> — alguém
precisa fazer algo AGORA ao recebê-lo; qualquer alerta que não atenda
esse critério treina a equipe a ignorar o pager, o efeito exatamente
oposto do pretendido. A regra prática é alertar em SLI/SLO — a
experiência real do usuário — em vez de em CAUSAS intermediárias: CPU
alta sozinha não é necessariamente um incidente (pode estar processando
uma carga legítima sem afetar ninguém), mas latência percebida pelo
usuário quase sempre é. A técnica de multi-window multi-burn-rate (do
Google SRE Workbook) resolve uma tensão real: alertar rápido para uma
queima GRANDE do error budget (algo está seriamente errado agora) mas
mais devagar para queimas pequenas (pode ser ruído normal que se
resolve sozinho) — um único limiar fixo não capturaria as duas situações
adequadamente. E todo alerta deveria vir acompanhado de um link para um
runbook específico dizendo o que fazer ao recebê-lo — sem isso, quem
está de plantão às 3 da manhã precisa improvisar uma investigação do
zero, sem contexto prévio nenhum.</p>

<h3>11. O pipeline completo: um coletor central roteando para múltiplos backends</h3>
<pre><code># otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: {}
      http: {}
  prometheus:
    config:
      scrape_configs:
      - job_name: app
        kubernetes_sd_configs: [{role: pod}]

processors:
  batch: {}
  resource:
    attributes:
    - key: env
      value: prod
      action: insert
  tail_sampling: { ... }

exporters:
  otlp/tempo: { endpoint: tempo:4317 }
  prometheus/mimir: { endpoint: 0.0.0.0:9090 }
  loki: { endpoint: http://loki:3100/loki/api/v1/push }

service:
  pipelines:
    traces: { receivers: [otlp], processors: [batch, tail_sampling], exporters: [otlp/tempo] }
    metrics: { receivers: [otlp, prometheus], processors: [batch, resource], exporters: [prometheus/mimir] }
    logs: { receivers: [otlp], processors: [batch], exporters: [loki] }</code></pre>
<p>Ter um único coletor central, em vez de cada aplicação exportando
diretamente para cada backend, é o que permite mudar de backend, ajustar
sampling ou adicionar processamento (como o atributo <code>env: prod</code>
inserido automaticamente aqui) sem tocar em nenhum código de
aplicação — a mudança fica inteiramente na configuração do coletor.</p>

<h3>12. Mapa de serviço automático: a topologia real, derivada dos próprios traces</h3>
<p>A partir do volume de traces coletados, ferramentas de observabilidade
constroem automaticamente um mapa mostrando quais serviços chamam quais
outros — "web chama auth e api; api chama postgres e redis" — sem que
ninguém precise manter esse diagrama manualmente atualizado (que
inevitavelmente ficaria desatualizado assim que a arquitetura mudasse).
Esse mapa é especialmente valioso durante incidentes: ver que "auth está
lento" imediatamente sugere quais serviços DOWNSTREAM provavelmente
também estão sofrendo, sem precisar perguntar a cada time individualmente
quem depende de quem. Datadog, Honeycomb, Grafana Tempo e Jaeger geram
essa visão automaticamente a partir dos mesmos dados de trace já
coletados.</p>

<h3>13. Sete anti-padrões que tornam observabilidade cara e ainda assim inútil</h3>
<ul>
<li><strong>Logs e métricas em silos, sem correlação</strong>: cada
investigação vira trabalho de detetive cego, correlacionando timestamps
manualmente entre sistemas diferentes.</li>
<li><strong>Cardinalidade explosiva em métricas</strong>: derruba a
própria infraestrutura de monitoramento, exatamente quando ela mais
seria necessária.</li>
<li><strong>100% de sampling sem necessidade real</strong>: custo de
armazenamento desproporcional ao valor extraído do volume extra.</li>
<li><strong>Alertas em causas em vez de sintomas</strong>: pager toca
por nada relevante, ou pior, fica em silêncio justamente quando o
usuário está sofrendo de verdade.</li>
<li><strong>Sem runbook por trás de cada alerta</strong>: quem está de
plantão é acordado com "CPU alta" e zero contexto sobre o que fazer a
respeito.</li>
<li><strong>Trace instrumentado só em alguns serviços</strong>: lacunas
na cobertura escondem exatamente a parte do sistema onde o problema
mora.</li>
<li><strong>Sem instrumentação customizada além da automática</strong>:
auto-instrumentação captura chamadas HTTP e de banco, mas nunca vê
lógica de NEGÓCIO específica (um desconto aplicado errado, uma regra de
elegibilidade), que só instrumentação manual revela.</li>
</ul>

<h3>14. Custo: onde cada pilar cresce, e como conter cada um</h3>
<p>Armazenamento de log cresce linearmente com o volume de tráfego — a
resposta operacional comum é reter pouco tempo "quente" (7 a 30 dias,
onde a busca é rápida) e mover o resto para um tier "frio" de arquivo
mais barato, mas com busca mais lenta. Métricas ficam sob controle
principalmente através de controlar cardinalidade (seção 6) — o custo
não é sobre volume de dados no tempo, é sobre número de séries
diferentes mantidas simultaneamente. Traces se beneficiam de sampling
agressivo combinado com tail-based (seção 7) para preservar justamente
os casos raros e caros de perder (erros, lentidão) sem pagar o custo de
guardar tudo. E para quem usa um fornecedor SaaS, o custo real costuma
ser calculado por GB ingerido MAIS por host monitorado — um modelo de
cobrança que pode escalar de forma surpreendente conforme a
infraestrutura cresce, e vale projetar antes de se comprometer com uma
plataforma específica.</p>"""
                ),
                "body_en": (
                """<h3>1. The three pillars: why none alone is enough to investigate an incident</h3>
<p><strong>Metrics</strong> are time series of aggregated numbers — "requests/second", "500 errors/second", "CPU%" — cheap to store and statistically powerful, but with necessarily low cardinality: they say WHAT is happening in aggregate, without detail of any specific request. <strong>Logs</strong> are discrete textual events ("login failed for user@x"), with far more detail than a metric can carry, but with proportionally higher storage cost and free-text search, not numeric aggregation. <strong>Traces</strong> are the span tree that represents the real PATH of a request across several services — the only of the three sources that answers "where did this specific call go, and where was time spent". Each pillar answers a different question; in an architecture with dozens of microservices, investigating an incident using only one of the three is like trying to reconstruct a crime seeing only the photo, only the audio, or only the video — the three TOGETHER, correlated (section 8), is what enables fast reasoning during a real incident.</p>
<div class="mermaid">
flowchart LR
    subgraph Pilares ["Três pilares"]
        Logs["Logs"]
        Metrics["Métricas"]
        Traces["Traces"]
    end
    Logs --> Correl["Correlacionados por trace_id"]
    Metrics --> Correl
    Traces --> Correl
</div>


<h3>2. Tracing: a request becomes a tree, not a log line</h3>
<p>An entire request is a <strong>trace</strong>; each operation inside it (an auth call, a DB query, a call to another service) is a <strong>span</strong>, and spans form a tree with an explicit parent-child relationship:</p>
<pre><code>POST /checkout                              [800ms]
├── auth.verify_token                       [10ms]
├── inventory.check_stock                   [30ms]
├── payment.charge                          [600ms]
│   ├── stripe.create_charge                [580ms]
│   └── db.write_charge                     [15ms]
├── notification.send_email                 [40ms]
└── db.write_order                          [20ms]</code></pre>
<p>Just looking at that tree, it is obvious WHERE the total 800ms were spent: <code>payment.charge</code> consumes 600ms, and inside it the external Stripe call (580ms) dominates — information that a "checkout average latency" metric would never reveal alone. Each span carries a <code>trace_id</code> (identifies the whole trace), a <code>span_id</code> (identifies this specific span), a <code>parent_span_id</code> (where it came from), start and end timestamps, service and operation name, status (ok/error), attributes (<code>http.method</code>, <code>db.statement</code>, <code>user.id</code>) and events (logs local to the span itself). Propagation between services follows the W3C TraceContext standard, carried in common HTTP headers:</p>
<pre><code>traceparent: 00-{trace-id-32-hex}-{parent-id-16-hex}-{flags-2-hex}
tracestate: rojo=00f067aa0ba902b7</code></pre>
<p>It is that header propagated from service to service that lets you reconstruct the entire tree afterwards — without it, each service would only know its own part, with no notion that they belong to the same original request.</p>

<h3>3. OpenTelemetry: a standard so you do not rewrite instrumentation on every backend swap</h3>
<p>OpenTelemetry (OTel, CNCF project) solves a real problem: before it, instrumenting code for a specific tracing backend meant rewriting that entire instrumentation if the company decided to switch vendors. The SDK, available in each language, instruments the code; auto-instrumentation covers common libraries (HTTP, database, RPC) WITHOUT requiring manual code changes; OTLP is the binary protocol (gRPC or HTTP) that carries data between the application and the collector; and the Collector is an agent that receives data in multiple formats (OTLP, Jaeger, Zipkin, Prometheus), processes it, and exports to ANY chosen backend — switching from Jaeger to Tempo, for example, becomes a collector config change, not a rewrite of instrumentation in every service:</p>
<pre><code># Python
$ pip install opentelemetry-distro opentelemetry-exporter-otlp
$ opentelemetry-bootstrap --action=install
$ OTEL_SERVICE_NAME=checkout \\
  OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \\
  opentelemetry-instrument python app.py
# pronto: traces para HTTP, requests, sqlalchemy, redis... aparecem no backend</code></pre>

<h3>4. Trace backends: each resolves a different cost/power trade-off</h3>
<p><strong>Jaeger</strong> is the classic CNCF backend, using Cassandra or Elasticsearch as storage — mature, but storage cost grows with trace volume. <strong>Tempo</strong> (Grafana) uses S3/GCS-based storage, dramatically cheaper for large volumes, at the cost of queries a bit less rich than solutions with a dedicated index. <strong>Zipkin</strong> was a pioneer (originated at Twitter) and is still used in legacy systems. <strong>Honeycomb</strong> is SaaS specialized in HIGH cardinality — enabling interactive queries exploring attribute combinations that traditional backends would not support well. <strong>Datadog APM</strong>, New Relic, and Dynatrace are complete commercial SaaS platforms covering the three pillars under a single subscription. <strong>SigNoz</strong> and <strong>Uptrace</strong> are open-source self-hosted alternatives for those who want control without recurring SaaS cost.</p>

<h3>5. Metrics: why the average hides exactly the problem you need to see</h3>
<p>Working with histograms instead of averages is the difference between knowing a problem exists and knowing how severe it is for a real fraction of users:</p>
<pre><code>avg_latency = 100ms                    # parece bom
p50 = 50ms
p99 = 5s                                # 1% dos usuários: experiência terrível</code></pre>
<p>A 100ms average looks perfectly healthy — but a p99 of 5 seconds reveals that 1% of users (which can be a large absolute number, depending on traffic) have a terrible experience the average alone completely hides. Three complementary mental models help decide WHAT to measure: RED (from Tom Wilkie), focused on SERVICES — Rate (requests/second), Errors (errors/second), Duration (latency distribution); USE (from Brendan Gregg), focused on RESOURCES — Utilization (percent used), Saturation (accumulated wait queue), Errors (errors of the resource itself); and Google SRE's Four Golden Signals — latency, traffic, errors, saturation, essentially a synthesis of the previous two adapted for any service.</p>

<h3>6. Cardinality: the trap that takes down a poorly configured Prometheus</h3>
<p>Cardinality is the number of UNIQUE TIME SERIES a metric generates — each distinct combination of label values creates a new, separate series for the time-series database to store:</p>
<pre><code># RUIM
http_requests_total{user_id="123", path="/api/users/456"}
# 1M users * 100k paths = 100B séries → quebra Prometheus

# BOM
http_requests_total{route="/api/users/:id", method="GET", status="200"}
# poucas séries, alta utilidade</code></pre>
<p>Using <code>user_id</code> or the FULL path (with a specific ID) as a label looks harmless line by line, but multiplies combinations explosively — a million users times a hundred thousand different paths generates cardinality no Prometheus, Cortex, or Mimir can operationally handle. The PARAMETERIZED route (<code>/api/users/:id</code> instead of the literal ID) keeps cardinality low and still delivers useful aggregated information. High-cardinality detail — WHICH specific user, WHICH specific request — belongs in traces and logs, which are designed from the start to handle that volume differently from a time series.</p>

<h3>7. Sampling: collecting everything is expensive; collecting the wrong sample hides what matters</h3>
<p>Capturing 100% of traces produced by a high-traffic system has prohibitive storage cost in most cases — that is why sampling strategies exist, each with a distinct trade-off. <strong>Head-based</strong> decides on the FIRST call, randomly (for example, keep N% of everything) — simple to implement, but tends to miss exactly the rare and interesting cases (the occasional error, the exceptionally slow request), because the decision is made BEFORE knowing whether that trace would be interesting. <strong>Tail-based</strong> inverts the logic: collect everything temporarily, and only decide AFTERWARDS, looking at the complete trace — deliberately prioritizing errors and slow requests, exactly the cases head-based tends to miss. The cost is operational: it requires a collector with a buffer, holding traces temporarily until the decision is made. <strong>Probabilistic</strong> is a simple fixed sample (for example, always 1%). And <strong>rate-limiting</strong> imposes an absolute ceiling of traces per second, per service, independent of total traffic volume:</p>
<pre><code># OTel Collector tail sampling
processors:
  tail_sampling:
    decision_wait: 30s
    policies:
    - name: errors-policy
      type: status_code
      status_code: { status_codes: [ERROR] }
    - name: slow-policy
      type: latency
      latency: { threshold_ms: 1000 }
    - name: random-policy
      type: probabilistic
      probabilistic: { sampling_percentage: 1 }</code></pre>
<p>This configuration combines the three strategies: always keep errors, always keep what is slow, and sample 1% of the rest — the most common pattern in production, because it preserves exactly the cases that matter most for debugging without paying the cost of keeping everything.</p>

<h3>8. Correlation: what turns three separate sources into a fast investigation</h3>
<p>Including the <code>trace_id</code> in EVERY log line is the link that connects the three observability sources:</p>
<pre><code>{"timestamp": "...", "level": "ERROR",
 "service": "payment", "trace_id": "4bf92f3577b34da6",
 "span_id": "00f067aa0ba902b7",
 "msg": "stripe charge failed", "user_id": "u-123"}</code></pre>
<p>With that correlation and a stack like Grafana with Loki (logs) + Tempo (traces) + Prometheus (metrics), the incident investigation flow becomes literally clickable: you see the error spike in a metric; drill down into that service's logs in the same time window; click the <code>trace_id</code> of a specific error log and land DIRECTLY on the matching trace; and in the trace, see exactly which span failed and how long each step took. Without that correlation, the same investigation would require manually correlating timestamps across three different systems — unviable at the speed a real incident demands.</p>

<h3>9. SLI, SLO and Error Budget: turning "is it working well?" into a numeric question</h3>
<p>An <strong>SLI</strong> (Service Level Indicator) is a metric that measures the real user experience — "percentage of requests under 500ms", for example. An <strong>SLO</strong> (Objective) is a numeric GOAL on that indicator — "99.9% of requests under 500ms in a 30-day window". The <strong>Error Budget</strong> is the arithmetic complement of the SLO: 100% minus 99.9% leaves 0.1% error margin, which for a 30-day window equals about 43 minutes of TOLERATED unavailability per month — and when that budget is being consumed too fast, the correct operational response is to FREEZE new deploys until the situation stabilizes, not keep shipping changes that increase risk. An <strong>SLA</strong> is the CONTRACTUAL commitment with the customer, typically defined looser than the internal SLO on purpose — the slack between the two is what lets the team detect and fix a problem BEFORE it violates the formal customer contract.</p>

<h3>10. Effective alerting: an alert that generates no action is noise, not signal</h3>
<p>An alert is only justified when it is <strong>actionable</strong> — someone needs to do something NOW upon receiving it; any alert that fails that criterion trains the team to ignore the pager, exactly the opposite of the intended effect. The practical rule is to alert on SLI/SLO — the real user experience — instead of on intermediate CAUSES: high CPU alone is not necessarily an incident (it may be processing legitimate load without affecting anyone), but user-perceived latency almost always is. The multi-window multi-burn-rate technique (from the Google SRE Workbook) resolves a real tension: alert quickly for a LARGE error-budget burn (something is seriously wrong now) but more slowly for small burns (may be normal noise that resolves itself) — a single fixed threshold would not capture both situations adequately. And every alert should come with a link to a specific runbook saying what to do upon receiving it — without that, whoever is on call at 3am has to improvise an investigation from scratch, with no prior context.</p>

<h3>11. The complete pipeline: a central collector routing to multiple backends</h3>
<pre><code># otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: {}
      http: {}
  prometheus:
    config:
      scrape_configs:
      - job_name: app
        kubernetes_sd_configs: [{role: pod}]

processors:
  batch: {}
  resource:
    attributes:
    - key: env
      value: prod
      action: insert
  tail_sampling: { ... }

exporters:
  otlp/tempo: { endpoint: tempo:4317 }
  prometheus/mimir: { endpoint: 0.0.0.0:9090 }
  loki: { endpoint: http://loki:3100/loki/api/v1/push }

service:
  pipelines:
    traces: { receivers: [otlp], processors: [batch, tail_sampling], exporters: [otlp/tempo] }
    metrics: { receivers: [otlp, prometheus], processors: [batch, resource], exporters: [prometheus/mimir] }
    logs: { receivers: [otlp], processors: [batch], exporters: [loki] }</code></pre>
<p>Having a single central collector, instead of each application exporting directly to each backend, is what lets you change backends, adjust sampling, or add processing (like the <code>env: prod</code> attribute inserted automatically here) without touching any application code — the change stays entirely in the collector configuration.</p>

<h3>12. Automatic service map: the real topology, derived from the traces themselves</h3>
<p>From the volume of collected traces, observability tools automatically build a map showing which services call which others — "web calls auth and api; api calls postgres and redis" — without anyone needing to keep that diagram manually updated (which would inevitably go stale as soon as the architecture changed). That map is especially valuable during incidents: seeing that "auth is slow" immediately suggests which DOWNSTREAM services are probably also suffering, without asking each individual team who depends on whom. Datadog, Honeycomb, Grafana Tempo, and Jaeger generate that view automatically from the same already-collected trace data.</p>

<h3>13. Seven anti-patterns that make observability expensive and still useless</h3>
<ul>
<li><strong>Logs and metrics in silos, without correlation</strong>: every investigation becomes blind detective work, correlating timestamps manually across different systems.</li>
<li><strong>Explosive cardinality in metrics</strong>: takes down the monitoring infrastructure itself, exactly when it would be most needed.</li>
<li><strong>100% sampling without real need</strong>: storage cost disproportionate to the value extracted from the extra volume.</li>
<li><strong>Alerts on causes instead of symptoms</strong>: the pager rings for nothing relevant, or worse, stays silent exactly when the user is truly suffering.</li>
<li><strong>No runbook behind each alert</strong>: whoever is on call is woken with "high CPU" and zero context about what to do about it.</li>
<li><strong>Trace instrumented only in some services</strong>: coverage gaps hide exactly the part of the system where the problem lives.</li>
<li><strong>No custom instrumentation beyond the automatic</strong>: auto-instrumentation captures HTTP and database calls, but never sees specific BUSINESS logic (a discount applied wrong, an eligibility rule), which only manual instrumentation reveals.</li>
</ul>

<h3>14. Cost: where each pillar grows, and how to contain each one</h3>
<p>Log storage grows linearly with traffic volume — the common operational response is to retain little "hot" time (7 to 30 days, where search is fast) and move the rest to a cheaper "cold" archive tier, but with slower search. Metrics stay under control mainly by controlling cardinality (section 6) — the cost is not about data volume over time, it is about the number of different series kept simultaneously. Traces benefit from aggressive sampling combined with tail-based (section 7) to preserve exactly the rare cases that are expensive to lose (errors, slowness) without paying the cost of keeping everything. And for those using a SaaS vendor, the real cost is usually calculated per GB ingested PLUS per monitored host — a billing model that can scale surprisingly as infrastructure grows, and is worth projecting before committing to a specific platform.</p>
"""
                ),
                "practical": (
                    "Instrumente uma app Python com <code>opentelemetry-instrument python "
                    "app.py</code>. Configure exportador OTLP para Grafana Tempo. Faça uma "
                    "request que passe por 3 microserviços (use docker-compose). No Grafana, "
                    "navegue do log com erro → trace_id → span tree e identifique o gargalo de "
                    "latência. Configure alerta em p99 &gt; 1s queimando error budget de 99.9% SLO."
                ),
                "practical_en": (
                    "Instrument a Python app with <code>opentelemetry-instrument python app.py</code>. "
                    "Configure an OTLP exporter to Grafana Tempo. Make a request that goes through 3 "
                    "microservices (use docker-compose). In Grafana, navigate from the error log → trace_id → "
                    "span tree and identify the latency bottleneck. Configure an alert on p99 &gt; 1s burning "
                    "the error budget of a 99.9% SLO."
                ),
            },
            "materials": [
                m("OpenTelemetry", "https://opentelemetry.io/docs/", "docs", "", title_en="OpenTelemetry", description_en=""),
                m("Distributed Systems Observability (livro)", "https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/", "book", "", title_en="Distributed Systems Observability (book)", description_en=""),
                m("Honeycomb: Tracing 101", "https://www.honeycomb.io/blog/tracing-101", "article", "", title_en="Honeycomb: Tracing 101", description_en=""),
                m("Grafana Tempo", "https://grafana.com/docs/tempo/latest/", "docs", "", title_en="Grafana Tempo", description_en=""),
                m("Jaeger", "https://www.jaegertracing.io/docs/latest/", "docs", "", title_en="Jaeger", description_en=""),
                m("W3C TraceContext", "https://www.w3.org/TR/trace-context/", "docs", "Padrão de propagação de trace_id.", title_en="W3C TraceContext", description_en="Standard for trace_id propagation."),
                m("Google SRE Workbook", "https://sre.google/workbook/table-of-contents/", "book", "Alerting e SLOs.", title_en="Google SRE Workbook", description_en="Alerting and SLOs."),
            ],
            "questions": [
                q("Trace é:",
                  "Conjunto de spans que representa caminho de uma requisição.",
                  ["Uma única linha registrada num arquivo de log, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas.", "Uma métrica que mede o uptime geral do serviço, prática que gera falso senso de segurança no time.", "Só um registro relacionado à resolução de DNS, comportamento que só some quando alguém finalmente lê a documentação."],
                  "Cada span é uma operação; juntos formam árvore. Permite ver onde tempo é gasto.",
                  statement_en="A trace is:",
                  correct_en="A set of spans that represents a request's path.",
                  wrong_en=["A single line recorded in a log file, a shortcut that looks safe in isolation but breaks when combined with other systems.", "A metric that measures overall service uptime, a practice that creates a false sense of security on the team.", "Just a record related to DNS resolution, behavior that only goes away when someone finally reads the docs."],
                  explanation_en="Each span is an operation; together they form a tree. Lets you see where time is spent."),
                q("OpenTelemetry padroniza:",
                  "Coleta de métricas, logs e traces.",
                  ["Padroniza só a coleta de métricas do serviço.", "Padroniza só a coleta de logs gerados pelo serviço.", "Funciona só em projetos escritos na linguagem Java."],
                  "SDK + protocolo OTLP. Backend pode ser trocado sem mudar instrumentação.",
                  statement_en="OpenTelemetry standardizes:",
                  correct_en="Collection of metrics, logs, and traces.",
                  wrong_en=["Standardizes only the collection of service metrics.", "Standardizes only the collection of logs generated by the service.", "Only works on projects written in the Java language."],
                  explanation_en="SDK + OTLP protocol. The backend can be swapped without changing instrumentation."),
                q("Span attributes:",
                  "Tags que enriquecem contexto (route, user, db).",
                  ["Um tipo específico de algoritmo de criptografia.", "Um defeito registrado no sistema de rastreamento de bugs.", "Só o nome do container onde o span foi gerado."],
                  "Use atributos semânticos padronizados (HTTP, DB, RPC) para queries consistentes.",
                  statement_en="Span attributes:",
                  correct_en="Tags that enrich context (route, user, db).",
                  wrong_en=["A specific type of encryption algorithm.", "A defect recorded in the bug-tracking system.", "Just the name of the container where the span was generated."],
                  explanation_en="Use standardized semantic attributes (HTTP, DB, RPC) for consistent queries."),
                q("p99 vs avg:",
                  "p99 mostra cauda, onde mora a dor de muitos usuários.",
                  ["As duas métricas mostram exatamente a mesma informação.", "A média costuma ser considerada melhor que o p99.", "O p99 praticamente não importa para a experiência do usuário."],
                  "Média de 100ms com p99 de 5s = 1% dos usuários têm experiência terrível.",
                  statement_en="p99 vs avg:",
                  correct_en="p99 shows the tail, where many users' pain lives.",
                  wrong_en=["Both metrics show exactly the same information.", "The average is usually considered better than p99.", "p99 practically does not matter for the user experience."],
                  explanation_en="An average of 100ms with a p99 of 5s = 1% of users have a terrible experience."),
                q("Sampling em traces:",
                  "Reduz custo coletando subconjunto representativo.",
                  ["Substitui a necessidade de coletar métricas do serviço.", "Costuma aumentar bastante o custo de armazenamento.", "Descarta praticamente vários traces coletados."],
                  "Tail-based prioriza erros e slow paths. Head-based é mais simples.",
                  statement_en="Sampling in traces:",
                  correct_en="Reduces cost by collecting a representative subset.",
                  wrong_en=["Replaces the need to collect service metrics.", "Usually greatly increases storage cost.", "Discards practically several collected traces."],
                  explanation_en="Tail-based prioritizes errors and slow paths. Head-based is simpler."),
                q("Correlation entre logs e traces:",
                  "Use o trace_id em campos do log.",
                  ["Tecnicamente não é possível fazer esse tipo de correlação.", "Substitui a necessidade de configurar IAM na conta.", "Depende só da resolução de nomes DNS do serviço."],
                  "Loki + Tempo + Prometheus conseguem 'pular' entre os três por trace_id.",
                  statement_en="Correlation between logs and traces:",
                  correct_en="Use the trace_id in log fields.",
                  wrong_en=["Technically it is not possible to do that kind of correlation.", "Replaces the need to configure IAM on the account.", "Depends only on DNS name resolution for the service."],
                  explanation_en="Loki + Tempo + Prometheus can 'jump' across the three via trace_id."),
                q("Service map:",
                  "Visão das dependências entre serviços (a partir de traces).",
                  ["Um recurso disponível só na linguagem de consulta Cypher, suposição que só se sustenta enquanto o time é pequeno.", "Um tipo específico de configuração de TLS, prática ainda comum em sistema legado que raramente é atualizado.", "Um mapa físico da disposição dos racks no datacenter, comportamento que só vira prioridade depois que já causou prejuízo."],
                  "Datadog/Tempo/Jaeger geram automaticamente. Em incidente: 'qual serviço chama qual'.",
                  statement_en="Service map:",
                  correct_en="A view of dependencies between services (from traces).",
                  wrong_en=["A feature available only in the Cypher query language, an assumption that only holds while the team is small.", "A specific type of TLS configuration, a practice still common in rarely updated legacy systems.", "A physical map of rack layout in the datacenter, behavior that only becomes a priority after it has already caused damage."],
                  explanation_en="Datadog/Tempo/Jaeger generate it automatically. In an incident: 'which service calls which'."),
                q("RED method:",
                  "Rate, Errors, Duration, métricas para serviços.",
                  ["Um mecanismo de backup dos dados do serviço, erro típico de configuração feita às pressas, sem revisão posterior.", "Uma camada de cache usada pelo serviço, comportamento que só vira prioridade depois que já causou prejuízo.", "Um conjunto de registros relacionados a DNS, atalho comum quando o prazo aperta e ninguém revisa depois."],
                  "Por endpoint. Combina com USE para visão completa.",
                  statement_en="RED method:",
                  correct_en="Rate, Errors, Duration — metrics for services.",
                  wrong_en=["A backup mechanism for service data, a typical mistake from configuration done in a rush without later review.", "A cache layer used by the service, behavior that only becomes a priority after it has already caused damage.", "A set of records related to DNS, a common shortcut when the deadline is tight and nobody reviews later."],
                  explanation_en="Per endpoint. Combine with USE for a complete view."),
                q("Cardinalidade alta:",
                  "Pode quebrar backends de métricas.",
                  ["Praticamente não faz diferença para o backend usado.", "Costuma acelerar bastante as consultas feitas ao backend.", "Costuma reduzir o custo de armazenamento do backend."],
                  "Cada combinação única de labels = série. user_id em métrica = milhões de séries.",
                  statement_en="High cardinality:",
                  correct_en="Can break metrics backends.",
                  wrong_en=["Practically makes no difference to the backend in use.", "Usually greatly speeds up queries made to the backend.", "Usually reduces the backend's storage cost."],
                  explanation_en="Each unique label combination = a series. user_id on a metric = millions of series."),
                q("OTel Collector:",
                  "Pipeline configurável de receivers/processors/exporters.",
                  ["Um ambiente de desenvolvimento integrado (IDE).", "Um substituto direto e completo do próprio Kubernetes.", "Um banco de dados usado para guardar métricas históricas."],
                  "Um único agente que recebe OTLP/Jaeger/Zipkin e exporta para múltiplos backends.",
                  statement_en="OTel Collector:",
                  correct_en="A configurable pipeline of receivers/processors/exporters.",
                  wrong_en=["An integrated development environment (IDE).", "A direct and complete substitute for Kubernetes itself.", "A database used to store historical metrics."],
                  explanation_en="A single agent that receives OTLP/Jaeger/Zipkin and exports to multiple backends."),
            ],
        },
        # =====================================================================
        # 5.8 Security Chaos Engineering
        # =====================================================================
        {
            "title": "Security Chaos Engineering",
            "title_en": "Security Chaos Engineering",
            "summary": "Derrubar partes do sistema para ver se ele resiste.",
            "summary_en": "Break parts of the system to see if it holds.",
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
                "intro_en": (
                    "You have alerts, runbooks, NetworkPolicy, backup. Everything on paper looks great. But "
                    "does it work <em>for real</em>? Chaos engineering answers empirically: it introduces "
                    "controlled failures to find weaknesses before a real incident. It was born at Netflix in "
                    "2010 (Chaos Monkey). Security chaos extends the idea to validate defensive controls — "
                    "tests whether the SOC detects simulated exfil, whether the runbook works in an "
                    "intrusion, whether isolation survives an entire zone going down."
                ),
                "body": (
                """<h3>1. Os cinco princípios que separam experimento de vandalismo</h3>
<p>Chaos engineering não é "quebrar coisas para ver o que acontece" — é
um método científico aplicado a sistemas em produção, com cinco passos
que, pulados, transformam o experimento em teatro sem valor real:</p>
<div class="mermaid">
flowchart LR
    A["Hipótese: sistema resiste a X"] --> B["Experimento controlado"]
    B --> C{"Sistema se comportou como esperado?"}
    C -- "Sim" --> D["Confiança confirmada"]
    C -- "Não" --> E["Fraqueza real encontrada, corrige"]
</div>

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
                "body_en": (
                """<h3>1. The five principles that separate experiment from vandalism</h3>
<p>Chaos engineering is not "break things to see what happens" — it is a scientific method applied to production systems, with five steps that, when skipped, turn the experiment into theater with no real value:</p>
<div class="mermaid">
flowchart LR
    A["Hipótese: sistema resiste a X"] --> B["Experimento controlado"]
    B --> C{"Sistema se comportou como esperado?"}
    C -- "Sim" --> D["Confiança confirmada"]
    C -- "Não" --> E["Fraqueza real encontrada, corrige"]
</div>

<ol>
<li><strong>Define the steady state</strong>: a MEASURABLE metric of system health — request success rate, p99 latency, error rate. Without that numeric baseline, there is no way to distinguish "the experiment caused a real regression" from "it was always like that" — the comparison simply does not exist.</li>
<li><strong>Raise a falsifiable hypothesis</strong>: "killing 1 web pod does not impact the SLI" is a statement the experiment itself can refute. "Let's see what happens" is not a hypothesis — it is the absence of a question, and without a question there is no directed learning, only passive observation.</li>
<li><strong>Introduce real-world events</strong>: network latency, loss of an entire zone, cache corruption, expired certificate — the failures that REALLY happen in production, not artificial failures that would never occur on their own.</li>
<li><strong>Limit the blast radius</strong>: start tiny — 1 pod, 1 namespace, 1 region — and have a kill switch able to stop everything instantly. That is the difference between a controlled experiment and a self-induced incident.</li>
<li><strong>Learn and act</strong>: an experiment that reveals a failure but generates no concrete fix afterwards is theater — validation only has value if someone actually closes the hole found.</li>
</ol>

<h3>2. Steady state in practice: what makes a metric good or bad</h3>
<p>A steady-state metric needs to reflect what the USER feels, not what is easy to measure internally. "p99 latency under 500ms on the /checkout route" and "success rate above 99.5%" are good because they connect directly to a real experience — if the experiment degrades either, you know something that matters broke. "Low CPU" and "logs without error" are bad metrics for this purpose: low CPU says nothing about whether the user is getting correct responses (a hung system also has low CPU), and "error-free" logs only prove nobody logged the error — not that it did not happen.</p>

<h3>3. Three experiment categories, three types of weakness</h3>
<p><strong>Resilience</strong> experiments test infrastructure against infrastructure failures: kill pods, inject network latency, take down DNS, simulate loss of an entire availability zone, fail the primary database, cool the cache. <strong>Security</strong> experiments test DEFENSIVE CONTROLS against simulated attacks: deliberate credential leak, data exfiltration attempt, simulated pod compromise, container escape attempt. <strong>Operational</strong> experiments test the TEAM, not the system: take down the primary paging channel (does the secondary work?), take the on-call person offline (does the next on the roster respond?), force someone to act without the runbook at hand (does improvisation hold?). The three categories answer different questions — a mature chaos engineering program covers all three, not only the easiest to automate.</p>

<h3>4. The tool ecosystem, by usage category</h3>
<p>For Kubernetes clusters, <strong>Chaos Mesh</strong> (CNCF project) exposes each failure type as a native CRD — <code>PodChaos</code>, <code>NetworkChaos</code>, <code>IOChaos</code>, <code>KernelChaos</code>, <code>TimeChaos</code> — which means versioning experiments in Git the same way as any other cluster manifest (seen in sections 5 and 6). <strong>LitmusChaos</strong> is the equivalent CNCF alternative, with a hub of ready experiments to reuse. Outside Kubernetes, cloud providers have dedicated services — <strong>AWS Fault Injection Simulator</strong> for EC2/ECS/EKS/RDS, <strong>Azure Chaos Studio</strong> and GCP equivalents — that inject failure directly into the managed infrastructure layer, without needing an agent running inside the cluster. <strong>Gremlin</strong> is the most mature multi-cloud commercial option on the market. Netflix's <strong>ChaosMonkey/Simian Army</strong> was the pioneer (2010) and inspired this entire tool category. <strong>ChaoSlingr</strong> focuses specifically on security experiments, the central theme of this lesson. <strong>Toxiproxy</strong> (Shopify) is a simple TCP proxy that injects latency and packet loss, useful for reproducing network failures in a local development environment, without needing an entire cluster.</p>

<h3>5. Chaos Mesh example: kill random pods on a schedule</h3>
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
<p>The <code>scheduler</code> with cron syntax turns this experiment into a CONTINUOUS one, not a one-off event fired manually — the cluster starts living with pods dying unpredictably all the time, exactly the kind of constant stress that exposes hidden dependencies (a service that assumes the pod it called will always be there) much earlier than an isolated test.</p>

<h3>6. Example: network latency between services, and what to ask afterwards</h3>
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
<p>Injecting 100ms of artificial latency between the API and the database is not the experiment itself — it is the TRIGGER for the questions that really matter: does p99 rise proportionally or disproportionately (indicating a hidden bottleneck, like a connection pool that is too small)? Do the configured circuit breakers actually fire in this scenario, or do they only exist on paper? Do real users perceive an error, or does the system absorb the degradation gracefully? Do the alerts configured for "high latency" fire AT that specific moment, or would they only fire with a much higher latency than the one tested?</p>

<h3>7. Game Day: the same scientific principle, applied to the team</h3>
<p>A Game Day is a simulated scenario — in controlled production or in a room via tabletop — designed to test the TEAM, not only the system. The script follows the same scientific-method logic from section 1: in the <strong>pre-game</strong> phase, a facilitator defines hypothesis, blast radius, and metrics, but the responding team does NOT know the specific details — testing against a known script beforehand measures nothing real. At <strong>game start</strong>, the failure is injected for real (in staging) or narrated (tabletop). The <strong>detection</strong> phase measures MTTD (mean time to detect): how long until the team notices via real channels — alerts, dashboards, customer complaint — without an external hint. The <strong>response</strong> measures MTTR (mean time to recover): how long until the real runbook is applied and the problem solved. The <strong>recovery</strong> phase confirms that the steady state defined in the hypothesis returned. The final <strong>postmortem</strong> captures what worked, what failed, and becomes concrete action. The most common findings in real Game Days are almost always the same: misconfigured alerts (fired late, or never fired), outdated runbooks (reference a system that already changed), hidden dependencies (nobody knew service X depended on Y), and escalation paths that simply do not exist when someone needs them.</p>

<h3>8. Security chaos: validate the control, not only the infrastructure</h3>
<p>The central difference of SECURITY chaos versus resilience chaos is that here the experiment's target is a DEFENSIVE CONTROL, not an infrastructure component. Deliberately "forgetting" an AWS key in a public test repository measures three chained response times: how long until the CI's own secret scanner alerts, how long until GitHub automatically revokes, and how long until the SOC notices via CloudTrail that that credential was used from somewhere unexpected — each defense layer tested in isolation. Simulating exfiltration by having a pod call a "canary" domain (controlled, for observation) tests whether DLP or the SIEM really detect suspicious outbound traffic, or would only detect it in a theoretical report. Simulating a privilege-escalation attempt (a <code>setuid</code> inside a container, for example) directly tests whether Falco (or equivalent) actually generates the alert it should. Introducing a ServiceAccount with temporary <code>cluster-admin</code> tests whether RBAC auditing detects the anomaly. And an image with a disguised cryptominer tests whether image scanning and the admission policy (seen in the Admission Controllers lesson) really block before deploy, not only in theory.</p>

<h3>9. Chaos in production: yes, but with a kill switch tested before you need it</h3>
<p>Running chaos engineering directly in production is safe when followed by a progression: start in development and staging until you gain confidence in tool behavior and blast-radius limits. Only then advance to an isolated Game Day in production, with a time window COMMUNICATED to all relevant stakeholders ("on day X at Y, we will take down an entire zone in region Z for 15 minutes"). The kill switch — a single command able to interrupt the entire experiment instantly — must be TESTED before the first real experiment, not only exist in theory; a kill switch that was never triggered is as reliable as a backup that was never restored. Always have a plan B for the scenario where the experiment becomes a real incident. Netflix has operated <strong>continuous chaos</strong> in production for years — the final maturity stage, where the blast radius is small enough to run all the time without relevant risk.</p>

<h3>10. Metrics: how to prove the chaos program is worth the investment</h3>
<p>MTTD and MTTR (defined in section 7) are the central metrics — the lower over time, the faster the team detects and recovers from real problems, not only simulated ones. "Findings per experiment" counts concrete discoveries: runbook bugs, alerts that should have fired and did not, hidden dependencies revealed. "Action items completed" measures whether discoveries actually become fixes, or only get recorded and forgotten (the anti-pattern from section 12). The hardest metric to capture — but the final justification of the entire program — is the reduction of REAL incidents after chaos engineering started: proving causality requires comparing long periods, but it is the number that convinces whoever funds the program that it is worth the effort.</p>

<h3>11. The maturity pyramid: where most teams should start</h3>
<ol>
<li><strong>Tabletop exercises</strong>: narrated scenario in a room, without touching any system. Easy, no risk, the right starting point for any team that has never done this.</li>
<li><strong>Manual chaos in dev/staging</strong>: small controlled failures, still far from production.</li>
<li><strong>Scheduled game days in production</strong>: communicated window, limited blast radius, but already in the real environment.</li>
<li><strong>Continuous chaos in production</strong> with a small blast radius — failures happening all the time, in an automated and safe way.</li>
<li><strong>Chaos as culture</strong>: each team maintains its own experiments, without depending on a central team to run them.</li>
</ol>
<p>Skipping stages — going straight to continuous chaos in production without ever having done a tabletop — usually ends in the first anti-pattern of section 12: a blast radius that is too large on the first attempt, the team loses confidence in the whole practice, and the program dies before maturing.</p>

<h3>12. Five ways the program fails before generating value</h3>
<ul>
<li><strong>Chaos without a hypothesis</strong>: "let's see what happens" is vandalism, not experiment — without a specific question, any result looks "interesting" but teaches nothing actionable.</li>
<li><strong>No postmortem with concrete action</strong>: the experiment reveals a real hole, but nobody closes it afterwards — the next chaos round will find the SAME problem, and the organization learned nothing.</li>
<li><strong>Giant blast radius on the first attempt</strong>: a poorly calibrated experiment that takes down more than it should on debut makes the team lose confidence in the whole practice, and frequently kills the program before it matures.</li>
<li><strong>Chaos without coordinating with the SOC</strong>: if the security team does not know an experiment is running, the real alerts it fires are dismissed as "just another test" — including when, by coincidence, a real attack happens in the same window.</li>
<li><strong>Only resilience chaos, never security chaos</strong>: exhaustively testing infrastructure against failure and never testing defense controls against an attacker leaves half the value of the whole practice on the table.</li>
</ul>
"""
                ),
                "practical": (
                    "Use Chaos Mesh para injetar 100ms de latência em chamadas para o DB de "
                    "uma aplicação em staging por 10 minutos. Meça impacto em p99 e veja se "
                    "alertas configurados disparam. Em seguida, faça experimento de pod-kill "
                    "aleatório a cada 5 min por 1 hora e veja se o cluster recupera. Documente "
                    "em postmortem: hipótese, métricas, findings, action items."
                ),
                "practical_en": (
                    "Use Chaos Mesh to inject 100ms of latency into calls to an application's DB in staging "
                    "for 10 minutes. Measure the impact on p99 and see whether configured alerts fire. Then "
                    "run a random pod-kill experiment every 5 min for 1 hour and see whether the cluster "
                    "recovers. Document in a postmortem: hypothesis, metrics, findings, action items."
                ),
            },
            "materials": [
                m("Principles of Chaos", "https://principlesofchaos.org/", "article", "", title_en="Principles of Chaos", description_en=""),
                m("Chaos Mesh", "https://chaos-mesh.org/docs/", "docs", "", title_en="Chaos Mesh", description_en=""),
                m("LitmusChaos", "https://litmuschaos.io/docs/", "docs", "", title_en="LitmusChaos", description_en=""),
                m("Gremlin", "https://www.gremlin.com/community/", "article", "", title_en="Gremlin", description_en=""),
                m("ChaosSlingr (security)", "https://github.com/Optum/ChaoSlingr", "tool", "", title_en="ChaosSlingr (security)", description_en=""),
                m("AWS Fault Injection Simulator", "https://docs.aws.amazon.com/fis/latest/userguide/what-is.html", "docs", "", title_en="AWS Fault Injection Simulator", description_en=""),
                m("Chaos Engineering: Crash course", "https://www.gremlin.com/chaos-engineering", "course", "Curso introdutório.", title_en="Chaos Engineering: Crash course", description_en="Introductory course."),
            ],
            "questions": [
                q("Chaos engineering:",
                  "Experimentos controlados para descobrir fraquezas.",
                  ["Testes rodados sem alguma hipótese definida antes.", "Apagar dados de produção de forma direta e sem plano.", "Invadir o sistema usando ações completamente aleatórias."],
                  "Não é vandalismo: cada experimento tem hipótese, métrica e blast radius.",
                  statement_en="Chaos engineering:",
                  correct_en="Controlled experiments to discover weaknesses.",
                  wrong_en=["Tests run without any hypothesis defined beforehand.", "Deleting production data directly and without a plan.", "Breaking into the system using completely random actions."],
                  explanation_en="It is not vandalism: each experiment has a hypothesis, a metric, and a blast radius."),
                q("Game day:",
                  "Cenário simulado para testar runbooks e o time.",
                  ["Um processo de backup rodado de forma automática.", "Uma confraternização organizada pelo time de plantão.", "Um ataque de negação de serviço feito contra o público."],
                  "Pratica resposta sem o estresse de incidente real. Identifica buracos em runbooks.",
                  statement_en="Game day:",
                  correct_en="A simulated scenario to test runbooks and the team.",
                  wrong_en=["A backup process run automatically.", "A social gathering organized by the on-call team.", "A denial-of-service attack against the public."],
                  explanation_en="Practices response without the stress of a real incident. Finds holes in runbooks."),
                q("Hipótese científica:",
                  "Necessária antes do experimento.",
                  ["Algo que inviabiliza a realização de qualquer experimento.", "Algo relevante só dentro do contexto acadêmico.", "Um detalhe sem muita importância para o resultado final."],
                  "Sem hipótese, qualquer resultado é 'descoberta interessante', mas não testável.",
                  statement_en="Scientific hypothesis:",
                  correct_en="Required before the experiment.",
                  wrong_en=["Something that makes any experiment impossible to run.", "Something relevant only in an academic context.", "A detail of little importance to the final result."],
                  explanation_en="Without a hypothesis, any result is an 'interesting discovery', but not testable."),
                q("Blast radius:",
                  "Limite de impacto do experimento.",
                  ["Um limite que só se aplica ao ambiente de dev.", "Um limite que geralmente acaba cobrindo o sistema inteiro.", "Um limite restrito só à resolução de nomes DNS."],
                  "Comece pequeno (1 pod), expanda gradualmente. Tenha kill switch.",
                  statement_en="Blast radius:",
                  correct_en="The impact limit of the experiment.",
                  wrong_en=["A limit that only applies to the dev environment.", "A limit that usually ends up covering the entire system.", "A limit restricted only to DNS name resolution."],
                  explanation_en="Start small (1 pod), expand gradually. Have a kill switch."),
                q("Exfiltração simulada:",
                  "Verifica detecção/resposta como em ataque real.",
                  ["Substitui a necessidade de manter trilhas de audit.", "Um cenário que costuma ser bloqueado antes de rodar.", "Um exercício que não agrega valor real ao time."],
                  "Red team injeta tráfego para domínio suspeito; SOC deveria detectar.",
                  statement_en="Simulated exfiltration:",
                  correct_en="Checks detection/response as in a real attack.",
                  wrong_en=["Replaces the need to keep audit trails.", "A scenario that is usually blocked before it runs.", "An exercise that adds no real value to the team."],
                  explanation_en="Red team injects traffic to a suspicious domain; the SOC should detect it."),
                q("Métrica chave:",
                  "MTTD (mean time to detect) e MTTR.",
                  ["Só o custo financeiro estimado do incidente.", "O número de requisições por segundo do serviço.", "O tamanho em disco do arquivo de log gerado."],
                  "Detectar e recuperar rápido = menor impacto. Chaos mede ambos.",
                  statement_en="Key metric:",
                  correct_en="MTTD (mean time to detect) and MTTR.",
                  wrong_en=["Only the estimated financial cost of the incident.", "The number of requests per second of the service.", "The on-disk size of the generated log file."],
                  explanation_en="Detect and recover fast = smaller impact. Chaos measures both."),
                q("Chaos em prod:",
                  "Sim, com cuidado e plano de rollback.",
                  ["Um experimento que costuma ser geralmente destrutivo.", "Uma prática sem alguma necessidade real de existir.", "Uma prática que não deveria ser feita nesse ambiente."],
                  "Netflix faz há anos. Comece em janelas controladas com kill switch.",
                  statement_en="Chaos in prod:",
                  correct_en="Yes, carefully and with a rollback plan.",
                  wrong_en=["An experiment that tends to be generally destructive.", "A practice with no real need to exist.", "A practice that should not be done in that environment."],
                  explanation_en="Netflix has done it for years. Start in controlled windows with a kill switch."),
                q("LitmusChaos é:",
                  "Plataforma OSS para chaos em K8s.",
                  ["Um substituto direto e completo do Argo CD.", "Um mecanismo de backup do estado do cluster.", "Um ambiente de desenvolvimento integrado (IDE)."],
                  "CNCF incubating. CRDs para experimentos versionados em Git.",
                  statement_en="LitmusChaos is:",
                  correct_en="An OSS platform for chaos on K8s.",
                  wrong_en=["A direct and complete substitute for Argo CD.", "A backup mechanism for cluster state.", "An integrated development environment (IDE)."],
                  explanation_en="CNCF incubating. CRDs for experiments versioned in Git."),
                q("Sem aprendizado pós-experimento:",
                  "Chaos vira teatro.",
                  ["Uma consequência considerada inevitável do processo.", "Uma prática que continua agregando valor real ao time.", "Um cenário que dificilmente chega a acontecer na prática."],
                  "Ação real (corrigir, melhorar runbook, automatizar) é o propósito.",
                  statement_en="Without post-experiment learning:",
                  correct_en="Chaos becomes theater.",
                  wrong_en=["A consequence considered inevitable in the process.", "A practice that keeps adding real value to the team.", "A scenario that hardly ever happens in practice."],
                  explanation_en="Real action (fix, improve the runbook, automate) is the purpose."),
                q("Postmortem em chaos:",
                  "Captura findings e ações de resiliência.",
                  ["Uma decisão tomada sozinha por uma única pessoa.", "Algo relevante só quando houve downtime real no sistema.", "Substitui a necessidade de rodar o experimento em si."],
                  "Mesmo experimento bem-sucedido gera lições. Documente.",
                  statement_en="Postmortem in chaos:",
                  correct_en="Captures findings and resilience actions.",
                  wrong_en=["A decision made alone by a single person.", "Something relevant only when there was real system downtime.", "Replaces the need to run the experiment itself."],
                  explanation_en="Even a successful experiment generates lessons. Document them."),
            ],
        },
        # =====================================================================
        # 5.9 Incident Response
        # =====================================================================
        {
            "title": "Incident Response",
            "title_en": "Incident Response",
            "summary": "Automação para bloquear ataques automaticamente.",
            "summary_en": "Automation to block attacks automatically.",
            "lesson": {
                "intro": (
                    "Quando o incidente acontece, e vai acontecer, o tempo conta em minutos, "
                    "não horas. Equipes que praticam respondem em 10 min; equipes que não "
                    "praticam levam 10 horas. A diferença não é talento; é preparação. "
                    "Runbooks, papéis claros, comunicação coordenada e automação podem "
                    "reduzir MTTR (mean time to recover) drasticamente. Este tópico cobre o "
                    "framework NIST 800-61 e práticas modernas (SOAR, blameless postmortem)."
                ),
                "intro_en": (
                    "When the incident happens — and it will — time counts in minutes, not hours. Teams that "
                    "practice respond in 10 min; teams that don't practice take 10 hours. The difference is "
                    "not talent; it is preparation. Runbooks, clear roles, coordinated communication, and "
                    "automation can drastically reduce MTTR (mean time to recover). This topic covers the "
                    "NIST 800-61 framework and modern practices (SOAR, blameless postmortem)."
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
<div class="mermaid">
flowchart LR
    A["Preparation"] --> B["Detection e Analysis"]
    B --> C["Containment"]
    C --> D["Eradication"]
    D --> E["Recovery"]
    E --> F["Postmortem"]
    F --> A
</div>


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
                "body_en": (
                """<h3>1. NIST SP 800-61: why the framework is a cycle, not a list</h3>
<p>NIST structures incident response in four phases, and the detail many people miss is that the last phase FEEDS the first, closing a continuous-improvement cycle, not a linear checklist that ends at "resolved". <strong>Preparation</strong> is everything done BEFORE the incident happens — written runbooks, practiced drills, tools already configured, updated contacts, emergency ("break-glass") access ready to use. It is systematically the most underestimated phase, because it produces no visible short-term result — and precisely for that reason it is what most separates a team that responds in 10 minutes from one that takes 10 hours for the same incident. <strong>Detection & Analysis</strong> covers from the alert arriving through triage: distinguishing false positive from real incident, determining scope and severity. <strong>Containment, Eradication & Recovery</strong> is the action phase — limit the problem's advance, remove what caused it (a malicious artifact, a wrong configuration), restore the service. <strong>Post-Incident Activity</strong> — the blameless postmortem (section 7), resulting action items, runbook update — is what closes the cycle, feeding lessons learned back into Preparation. A team that skips that last phase repeats the same incidents indefinitely, because it never converts experience into prevention.</p>
<div class="mermaid">
flowchart LR
    A["Preparation"] --> B["Detection e Analysis"]
    B --> C["Containment"]
    C --> D["Eradication"]
    D --> E["Recovery"]
    E --> F["Postmortem"]
    F --> A
</div>


<h3>2. Roles in an incident: why the decision-maker should not touch the keyboard</h3>
<p>In small incidents, one person can accumulate several roles without a problem. In large incidents, separating roles stops being organization and becomes necessity: the person who DECIDES cannot simultaneously have "hands on keyboard" executing actions, because split attention between coordinating and executing is exactly where errors happen under pressure. The <strong>Incident Commander (IC)</strong> decides, coordinates, approves risky actions, and keeps the overall timeline view — deliberately WITHOUT touching any system, to keep the head free for decision. The <strong>Operations/Tech Lead</strong> is who actually executes the technical actions approved by the IC. The <strong>Communications</strong> function handles internal stakeholders, customers, and if needed the press, keeping the status page updated — without that dedicated function, the IC ends up answering stakeholder questions in the middle of a critical technical decision. The <strong>Scribe</strong> records the timeline in real time (a Slack thread, a shared document) — without that contemporaneous record, the postmortem depends on memory reconstructed AFTER the fact, systematically less accurate. In security incidents, a dedicated <strong>Security Lead</strong> preserves forensic evidence and coordinates the investigation, a responsibility distinct enough from general operational response to deserve its own role.</p>

<h3>3. Severity: why it must be defined before 3am</h3>
<p>Severity criteria serve a specific purpose: eliminate arbitrary decision at the moment of highest stress, when human judgment is most compromised. <strong>SEV1</strong> — total unavailability or severe data exposure, such as production down or a confirmed breach — pages 24/7 and immediate communication, without depending on someone deciding "is this serious enough?" in the heat of the moment. <strong>SEV2</strong> covers significant degradation (an entire region down, latency 5x normal) with expected response within an hour. <strong>SEV3</strong> is an isolated bug or partial problem, treatable in normal business hours. <strong>SEV4</strong> is cosmetic, low priority. Having those thresholds documented and agreed BEFORE the incident is what avoids the situation where two different people classify the same symptom completely differently — one "call everyone now" versus one "see tomorrow" — only because there was no explicit criterion to consult.</p>

<h3>4. Communication: a dedicated channel, not someone's personal Slack</h3>
<p>A specific channel per incident (<code>#inc-2026-04-25-auth-down</code>) preserves context and audit that a personal DM would never have — anyone who joins later can read the full history, and the organization keeps a searchable record of how each incident was conducted. A voice bridge (Zoom, Meet) serves for quick discussion that would be too slow by text. A public status page, updated periodically even with no real news, solves a known psychological problem: silence during an incident is interpreted by customers as a worse signal than an honest update saying "still investigating" — uncertainty bothers more than clear bad news. A recurring update template helps keep that rhythm without reinventing the wording every time:</p>
<pre><code>UPDATE 14:30 UTC: continuamos investigando latência elevada
no checkout. Times de pagamento e infra envolvidos. Próximo update: 15:00.</code></pre>
<p>An escalation matrix — documenting whom to call when the IC does not respond, at what point the executive level needs to be informed, when legal needs to join — avoids inventing those decisions on the spot, under pressure, for the first time.</p>

<h3>5. Containment: stop the bleeding before investigating in depth</h3>
<p>Short-term containment has a single goal: interrupt ongoing damage as fast as possible, even before understanding the full cause — isolate a compromised pod or host (via NetworkPolicy or taint), revoke a suspicious credential (kill a JWT, rotate a key), turn off a feature toggle causing the problem, or block a malicious IP at the WAF. Long-term containment already looks toward the eradication that comes next: take a snapshot or preserve forensic evidence BEFORE destroying anything (once destroyed, there is no way to investigate later), identify IOCs — indicators of compromise such as IPs, file hashes, domains — and map the real extent of the compromise, because acting on a smaller scope than the real one leaves hidden persistence that reappears later.</p>

<h3>6. Eradication and Recovery: why rotating "only what was compromised" is not enough</h3>
<p>Rebuilding images and containers from scratch, instead of "cleaning" existing ones, guarantees no malicious artifact survives hidden — manual cleanup of a potentially compromised system is a bet, rebuild from zero is a guarantee. Rotating ALL secrets within the affected scope — not only those proven leaked — recognizes a real investigation limit: proving a credential was NOT compromised is usually harder and slower than simply rotating it. Applying the root-vulnerability patch closes the door that allowed the original incident — without that, the same vector remains available for the next attack. Restoring from backup when there is destruction or ransomware requires that the backup was already tested beforehand (the Phase 3 backup lesson covers why). Validating that the service returned to steady state before declaring the incident closed avoids reopening the same incident hours later. And intensified monitoring for days after the incident detects a second wave or a return attempt by the same attacker, who rarely gives up on the first blocked try.</p>

<h3>7. Blameless postmortem: changing the question changes what you learn</h3>
<p>The difference between a postmortem that generates real improvement and one that only distributes blame is in the question it asks: "how did the SYSTEM allow a human error to cause impact?" instead of "who erred?". The second question produces defensiveness and hidden information next time; the first produces structural correction that prevents the NEXT person from making the same mistake, because the system — not the person — is the target of the fix. A complete postmortem has a 2-3 line executive summary (for whoever will not read the whole document), quantified impact (duration, percent of users affected, value lost, data exposed), a detailed timeline with timestamp of each action, root-cause analysis (5 Whys or fishbone diagram), what worked well (a frequently forgotten section, but important to preserve practices that already work), what can improve, and action items — each with owner, deadline, and trackable ticket. Without that last part, the document is only a well-written narrative that changes nothing in practice. A real "5 Whys" example shows how the technique descends from the surface to the structural cause:</p>
<pre><code>Sintoma: API ficou 30 min fora.
Por quê? Pod web entrou em CrashLoopBackOff.
Por quê? Liveness probe começou a falhar quando DB ficou lento.
Por quê? Probe fazia query no DB (acoplamento ruim).
Por quê? Template antigo da empresa, nunca questionado.
Por quê? Nenhuma revisão de templates desde 2 anos.
Action item: revisar todos templates de Deployment para liveness mais leve.</code></pre>
<p>Note that the real root cause is not "the probe failed" — it is "nobody has reviewed templates in two years", a PROCESS problem that the point technical fix (change the liveness probe) would not solve alone in other equally old templates.</p>

<h3>8. SOAR: automate the repetitive part of response, not the decision</h3>
<p>SOAR (Security Orchestration, Automation and Response) automates the MECHANICAL and repetitive steps of a response, leaving the final decision to a human: when an alert of a known type fires, the playbook automatically enriches the alert (looks up the IP in threat-intel bases, does GeoIP, WHOIS), checks whether it matches a known false-positive pattern, applies immediate containment if appropriate (block IP at the WAF, isolate the pod), opens a ticket, notifies the right channel — and only then waits for a person to decide whether the incident needs to escalate. The gain is not eliminating the human from the response, it is eliminating time spent on steps a machine executes in seconds and a human would take minutes repeating manually every time. Splunk SOAR (formerly Phantom), Tines, n8n, Shuffle, and Demisto are the most used tools in this category.</p>

<h3>9. Threat intelligence: defense that benefits from sharing</h3>
<p>An IOC (Indicator of Compromise) is any observable signal that points to malicious activity — hash of a malicious file, IP of a command-and-control server, suspicious domain, unusual user agent, or a behavior pattern. STIX/TAXII are the technical standards that allow exchanging those indicators between organizations in a structured way; MISP is the most used open-source platform to operate that exchange; ISACs (Information Sharing and Analysis Centers) organize that sharing by sector — FS-ISAC, for example, is specific to the financial sector. The logic of sharing IOCs with peers is a form of collective defense: an attack already identified by another company in the sector stops being "unknown" for whoever receives the indicator in time — and the same applies when receiving back.</p>

<h3>10. MITRE ATT&CK and D3FEND: a common vocabulary for attack and defense</h3>
<p>ATT&CK catalogs real tactics and techniques adversaries use, organized in a standardized way — instead of describing an attack in free prose ("the intruder managed to move laterally in a clever way"), a postmortem can map each observed step to a specific ATT&CK technique, making the report comparable across different incidents and different organizations. D3FEND is the defensive mirror: specific countermeasures mapped against each ATT&CK technique. In the Preparation phase, comparing which ATT&CK techniques the organization ALREADY covers with D3FEND countermeasures reveals defense gaps systematically, instead of depending on intuition about "what we still do not cover".</p>

<h3>11. Tabletop exercises: practice with no technical risk</h3>
<p>A tabletop is a purely verbal simulation — nothing is touched on a real system. A facilitator describes a scenario ("at 3am, an alert indicates a 10GB leak to a suspicious IP"), participants describe what they would do step by step, and the facilitator injects complications mid-way ("but the primary on-call is on vacation and the secondary does not respond") to test the plan B nobody had thought of. The discussion that emerges reveals real holes in runbook, communication, and escalation — at the same cost as a one-hour meeting, with no risk of causing a real incident by trying to simulate it. It is the lowest-cost, highest-return practice in this entire lesson, and that is why it is worth doing quarterly, not once a year.</p>

<h3>12. Postmortem culture: the hardest work to sustain</h3>
<p>Blameless culture is not a written policy, it is observable behavior over time — and it is systematically the hardest element to install in an organization, because it contradicts the human instinct to find who is responsible when something goes wrong. Real signals that the culture is working: writing a postmortem is not seen as punishment by whoever writes it; postmortems are shared openly inside the company, including with the executive level, instead of filed discreetly; the organization discusses "near misses" — incidents that almost happened but were avoided — with the same seriousness as real incidents, because the difference between the two is often luck, not competence; action items are actually tracked to completion, not only listed and forgotten; and there is no blame hunt — the starting premise is that each person acted with the best decision possible given the information they had AT THE MOMENT, not with the benefit of hindsight.</p>

<h3>13. The metrics that prove whether response is improving</h3>
<p>MTTD measures time to detection — the larger it is, the more time an attacker or a failure has to cause damage before someone notices; the realistic goal is minutes, not hours. MTTA measures time to acknowledgment (the "ack" from whoever receives the pager alert) — goal under 5 minutes, because an unrecognized alert is equivalent to no alert. MTTR measures time to full recovery — the goal varies by severity, but the trend over time matters more than the absolute number of an isolated incident. Incident frequency by severity reveals whether the system is becoming more or less fragile across months. Action items completed measures whether the improvement cycle (section 1) is actually closing, not only generating documents. And root-cause repetition — the SAME failure appearing for the third time — is the clearest signal of a systemic problem that no point fix truly solved.</p>

<h3>14. Seven anti-patterns that guarantee longer incidents</h3>
<ul>
<li><strong>No runbook</strong>: every incident becomes improvisation from scratch, at 3am, under the worst possible condition to think clearly.</li>
<li><strong>Never-tested runbook</strong>: a document written and never exercised has roughly a 50% chance of being outdated or wrong exactly when needed — the same logic as a never-restored backup.</li>
<li><strong>Communication by DM or personal WhatsApp</strong>: no audit, no searchable history, context lost as soon as the conversation scrolls down.</li>
<li><strong>IC with hands on the keyboard</strong>: nobody remains to coordinate the overall view while that person is focused on executing a specific technical action.</li>
<li><strong>Postmortem hunting for a culprit</strong>: guarantees the next person will hide relevant information instead of sharing it openly, exactly the opposite of what effective investigation needs.</li>
<li><strong>Action items with no owner or deadline</strong>: become a list of good intentions that never materializes into a real fix.</li>
<li><strong>Severity decided arbitrarily</strong>: the same type of symptom classified as SEV1 on one occasion and "see tomorrow" on another, only because there was no documented criterion to consult.</li>
</ul>

<h3>15. Pragmatic roadmap: from total absence of process to maturity</h3>
<ol>
<li>Define explicit severity criteria, documented, accessible to anyone who needs to classify an incident at 3am.</li>
<li>Implement incident channel, status page, and escalation matrix before the next incident happens, not during it.</li>
<li>Write runbooks for the five most likely scenarios — do not try to cover everything at once.</li>
<li>Run a monthly tabletop exercise to practice those runbooks without risk.</li>
<li>After every real incident, produce a postmortem within 5 business days — too much delay and details are already forgotten.</li>
<li>Automate via SOAR the playbooks that repeat most frequently, prioritizing by observed volume, not by guesswork.</li>
<li>Run quarterly Game Days combining chaos engineering (previous lesson) with real response practice.</li>
</ol>
"""
                ),
                "practical": (
                    "Crie runbook 'pod comprometido': aplique NetworkPolicy bloqueando egress, "
                    "adicione label <code>quarantine=true</code>, faça snapshot do pod, notifique "
                    "canal #incident. Automatize via webhook do Falco → workflow do Argo Events. "
                    "Em seguida, faça tabletop exercise com 2 colegas: 'às 2h chega alerta de "
                    "exfil de 5GB para domínio russo', pratique IC/Operations/Comms roles."
                ),
                "practical_en": (
                    "Create a 'compromised pod' runbook: apply a NetworkPolicy blocking egress, add label "
                    "<code>quarantine=true</code>, snapshot the pod, notify the #incident channel. Automate "
                    "via a Falco webhook → Argo Events workflow. Then run a tabletop exercise with 2 "
                    "colleagues: 'at 2am an alert arrives of 5GB exfil to a Russian domain', practice "
                    "IC/Operations/Comms roles."
                ),
            },
            "materials": [
                m("NIST SP 800-61r2", "https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final", "docs", "", title_en="NIST SP 800-61r2", description_en=""),
                m("Atlassian: Incident Mgmt Handbook", "https://www.atlassian.com/incident-management", "article", "", title_en="Atlassian: Incident Mgmt Handbook", description_en=""),
                m("PagerDuty Incident Response", "https://response.pagerduty.com/", "article", "", title_en="PagerDuty Incident Response", description_en=""),
                m("Google SRE: Incident Response", "https://sre.google/workbook/incident-response/", "book", "", title_en="Google SRE: Incident Response", description_en=""),
                m("MITRE D3FEND", "https://d3fend.mitre.org/", "docs", "", title_en="MITRE D3FEND", description_en=""),
                m("Postmortem template (Google)", "https://sre.google/sre-book/postmortem-culture/", "article", "", title_en="Postmortem template (Google)", description_en=""),
                m("MISP Threat Sharing", "https://www.misp-project.org/", "tool", "Plataforma de IOC.", title_en="MISP Threat Sharing", description_en="IOC platform."),
            ],
            "questions": [
                q("Primeira fase do NIST IR:",
                  "Preparation.",
                  ["Recovery.", "Eradication.", "Postmortem."],
                  "Tudo começa antes do incidente: runbooks, treinos, contatos atualizados, ferramentas prontas.",
                  statement_en="First phase of NIST IR:",
                  correct_en="Preparation.",
                  wrong_en=["Recovery.", "Eradication.", "Postmortem."],
                  explanation_en="Everything starts before the incident: runbooks, drills, updated contacts, tools ready."),
                q("MTTD mede:",
                  "Tempo para detectar incidente.",
                  ["Tempo para escrever postmortem.", "Tempo de cripto.", "Latência."],
                  "Se MTTD é horas, atacante já fez o estrago. Aim: minutos.",
                  statement_en="MTTD measures:",
                  correct_en="Time to detect an incident.",
                  wrong_en=["Time to write a postmortem.", "Crypto time.", "Latency."],
                  explanation_en="If MTTD is hours, the attacker already did the damage. Aim: minutes."),
                q("Runbook deve ser:",
                  "Acionável, versionado e testado em game days.",
                  ["Um documento pensado só na teoria, sem uso prático.", "Um documento compartilhado só por e-mail no time.", "Um documento confidencial que raramente chega a ser testado."],
                  "Sem teste, runbook tem 50% de chance de estar errado quando importa.",
                  statement_en="A runbook should be:",
                  correct_en="Actionable, versioned, and tested on game days.",
                  wrong_en=["A document designed only in theory, with no practical use.", "A document shared only by email within the team.", "A confidential document that is rarely ever tested."],
                  explanation_en="Without testing, a runbook has a 50% chance of being wrong when it matters."),
                q("Containment é:",
                  "Limitar avanço do invasor.",
                  ["Fazer um comunicado direto para a imprensa sobre o caso.", "Apagar evidências relacionadas ao incidente em andamento.", "Reiniciar o ambiente de produção inteiro sem análise."],
                  "Curto prazo: cortar acesso. Longo prazo: erradicar persistência.",
                  statement_en="Containment is:",
                  correct_en="Limiting the attacker's advance.",
                  wrong_en=["Issuing a direct press statement about the case.", "Deleting evidence related to the ongoing incident.", "Restarting the entire production environment without analysis."],
                  explanation_en="Short term: cut access. Long term: eradicate persistence."),
                q("Postmortem deve:",
                  "Ser blameless e gerar action items.",
                  ["Buscar identificar e punir a pessoa responsável.", "Ser mantido em sigilo dentro da liderança do time.", "Esconder o que de fato aconteceu durante o incidente."],
                  "Cultura de aprendizado é mais valiosa que culpado. Sem action item, postmortem é narrativa.",
                  statement_en="A postmortem should:",
                  correct_en="Be blameless and produce action items.",
                  wrong_en=["Seek to identify and punish the person responsible.", "Be kept secret within team leadership.", "Hide what actually happened during the incident."],
                  explanation_en="A learning culture is more valuable than a culprit. Without an action item, a postmortem is just a narrative."),
                q("SOAR automatiza:",
                  "Playbooks de resposta repetitivos.",
                  ["Substitui a necessidade de manter um antivírus ativo.", "Cuida só da resolução de nomes DNS durante o incidente.", "Substitui a necessidade de manter um SIEM configurado."],
                  "Tempo manual em incidente pequeno → segundos em pipeline.",
                  statement_en="SOAR automates:",
                  correct_en="Repetitive response playbooks.",
                  wrong_en=["Replaces the need to keep an antivirus active.", "Only handles DNS name resolution during the incident.", "Replaces the need to keep a SIEM configured."],
                  explanation_en="Manual time on a small incident → seconds in a pipeline."),
                q("Comunicação durante incidente:",
                  "Canal dedicado, bridge e quem assume comando.",
                  ["Resolver o incidente sem algum tipo de comunicação.", "Comunicar o incidente só por e-mail para o time.", "Coordenar a resposta usando o WhatsApp pessoal de alguém."],
                  "Sem command, time corre em direções diferentes. IC mantém ordem.",
                  statement_en="Communication during an incident:",
                  correct_en="A dedicated channel, bridge, and who takes command.",
                  wrong_en=["Resolving the incident without any kind of communication.", "Communicating the incident only by email to the team.", "Coordinating the response using someone's personal WhatsApp."],
                  explanation_en="Without command, the team runs in different directions. The IC keeps order."),
                q("Indicador de comprometimento (IOC):",
                  "Sinal observável (hash, IP, comportamento).",
                  ["Um tipo específico de configuração de TLS.", "A cadência com que os testes automatizados rodam.", "Só um registro relacionado à resolução de DNS."],
                  "Alimenta SIEM/EDR para detecção. Compartilhe via STIX/TAXII com peers.",
                  statement_en="Indicator of compromise (IOC):",
                  correct_en="An observable signal (hash, IP, behavior).",
                  wrong_en=["A specific type of TLS configuration.", "The cadence at which automated tests run.", "Just a record related to DNS resolution."],
                  explanation_en="Feeds SIEM/EDR for detection. Share via STIX/TAXII with peers."),
                q("Tabletop exercise:",
                  "Simulação discutida sem mexer em sistemas reais.",
                  ["Uma recriação física completa do incidente ocorrido.", "Um evento social organizado no estilo hackathon.", "Um exercício conduzido só com a presença do red team."],
                  "Fácil de organizar; revela gaps em runbook e comunicação rapidamente.",
                  statement_en="Tabletop exercise:",
                  correct_en="A discussed simulation without touching real systems.",
                  wrong_en=["A full physical recreation of the incident that occurred.", "A social event organized in hackathon style.", "An exercise run only with the red team present."],
                  explanation_en="Easy to organize; quickly reveals gaps in runbook and communication."),
                q("Severidade SEV1:",
                  "Indisponibilidade total ou exposição grave.",
                  ["Um aviso considerado de baixa relevância para o time.", "Um bug encontrado ainda em ambiente de desenvolvimento.", "Um pequeno erro visual na interface do usuário."],
                  "Convoca pager 24/7. Critérios devem estar documentados para evitar arbítrio.",
                  statement_en="SEV1 severity:",
                  correct_en="Total unavailability or severe exposure.",
                  wrong_en=["A warning considered of low relevance to the team.", "A bug found still in a development environment.", "A small visual error in the user interface."],
                  explanation_en="Pages 24/7. Criteria must be documented to avoid arbitrary calls."),
            ],
        },
        # =====================================================================
        # 5.10 Compliance Contínuo
        # =====================================================================
        {
            "title": "Compliance Contínuo",
            "title_en": "Continuous Compliance",
            "summary": "Garantir que o sistema segue leis (como a LGPD) o tempo todo.",
            "summary_en": "Ensure the system follows laws (like LGPD) all the time.",
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
                "intro_en": (
                    "Manual compliance in a spreadsheet does not scale. Annual audits that become a 3-month "
                    "nightmare are waste. <strong>Continuous compliance</strong> is applying the same DevOps "
                    "principles to audit: rules as code, automated evidence, real-time dashboards. Audit "
                    "stops being a traumatic event and becomes an almost-instant report. Covers LGPD, GDPR, "
                    "SOC 2, ISO 27001, PCI DSS — the frameworks most common in industry."
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
<div class="mermaid">
flowchart LR
    Infra["Infraestrutura em produção"] --> Check["Checagem automática contínua"]
    Check --> Compliant{"Está em conformidade?"}
    Compliant -- "Sim" --> Evidence["Evidência gerada automaticamente"]
    Compliant -- "Não" --> Fix["Alerta ou correção automática"]
</div>


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
                "body_en": (
                """<h3>1. Frameworks: why there are so many, and which applies to you</h3>
<p>Each compliance framework was born to solve a specific problem, and most companies need more than one at once. <strong>LGPD</strong> (General Data Protection Law, Brazil, 2018) regulates how personal data is processed — principles, legal bases, data-subject rights, controller/processor obligations — with fines that reach R$50 million per violation or 2% of revenue, enough to make non-compliance a real financial risk, not only reputational. <strong>GDPR</strong> is the European equivalent, with even larger fines (4% of global revenue or €20M) and applies to any company that processes EU citizens' data, even without a seat there. <strong>ISO 27001</strong> certifies an entire Information Security Management System (93 controls in Annex A), renewed by an accredited auditor annually — it is about a security PROCESS, not a specific law. <strong>SOC 2</strong> is the de facto standard for B2B SaaS in the US, with two levels: Type I evaluates control DESIGN at a point in time; Type II evaluates whether they actually WORKED over 6+ months — the second is what real enterprise customers demand, because it proves real operation, not intention on paper. <strong>PCI DSS</strong> applies to whoever touches card data, even when processing via Stripe — control scope shrinks, but does not disappear. <strong>HIPAA</strong> covers health data in the US, <strong>NIST CSF</strong> organizes security practices into five functions (Identify/Protect/Detect/Respond/Recover) voluntarily, and <strong>FedRAMP</strong> is the standard for selling to the US government cloud.</p>
<div class="mermaid">
flowchart LR
    Infra["Infraestrutura em produção"] --> Check["Checagem automática contínua"]
    Check --> Compliant{"Está em conformidade?"}
    Compliant -- "Sim" --> Evidence["Evidência gerada automaticamente"]
    Compliant -- "Não" --> Fix["Alerta ou correção automática"]
</div>


<h3>2. The ten LGPD principles: what each one prohibits in practice</h3>
<p>Each LGPD principle exists to block a specific behavior the law considers abusive. <strong>Purpose</strong> requires that processing have a legitimate, specific, and explicit purpose — "to improve our services" is too vague to serve as a real legal basis, because it does not delimit what will actually be done with the data. <strong>Adequacy</strong> requires that processing be compatible with that declared purpose — collecting a tax ID "to send a newsletter" would not be adequate. <strong>Necessity</strong> prohibits collecting more than the indispensable minimum: if a name solves it, asking for a tax ID is excess. <strong>Free access</strong> guarantees the data subject free consultation of their own data. <strong>Quality</strong> requires accurate and up-to-date data. <strong>Transparency</strong> requires that information about processing be accessible, not hidden in fine print. <strong>Security</strong> and <strong>prevention</strong> require concrete technical and administrative measures — not intention, but real control. <strong>Non-discrimination</strong> prohibits using data for discriminatory ends (denying credit by zip code, for example). And <strong>accountability</strong> requires that the company be able to DEMONSTRATE it adopted those measures, not only claim it did — it is the principle that makes all the audit and evidence in the rest of this lesson mandatory, not optional.</p>

<h3>3. Legal bases: why every processing needs one, documented</h3>
<p>Article 7 of LGPD lists ten possible legal bases — consent, compliance with legal obligation, contract performance, legitimate interest (among others) — and the practical rule that follows is simple to state and laborious to fulfill: EVERY personal-data processing needs to map to one of those bases, documented in a processing inventory. Without that mapping, a company cannot answer a regulator's most basic question — "why do you have this data?" — with a specific legal basis, only with generic justifications that do not survive a real audit.</p>

<h3>4. LGPD roles, and why confusing them is an expensive mistake</h3>
<p>The <strong>controller</strong> is who DECIDES the processing — the company that collects the data for its own purpose. The <strong>processor</strong> processes on behalf of the controller (AWS storing your data, a transactional email vendor) — and the processor does not decide purpose, only executes. That distinction matters because legal responsibility falls mainly on the controller, even when the incident happens in the processor's infrastructure — that is why the DPA (section 12) with each processor is not bureaucracy, it is the documentation that defines who answers for what. The <strong>DPO/Officer</strong> is the official contact point with ANPD (National Data Protection Authority) and with data subjects — name and contact disclosed publicly, not an anonymous internal role. The <strong>data subject</strong> is the natural person the data refers to — the center of everything else in the law.</p>

<h3>5. The nine data-subject rights, and how to operationalize them without becoming a manual process</h3>
<p>Article 18 guarantees the data subject confirming processing exists, accessing their data, correcting it, requesting anonymization/blocking/deletion, porting data to another service, deleting data processed by consent, knowing with whom the controller shared their data, knowing the consequences of denying consent, and revoking consent at any time. Handling each request manually — an email, a spreadsheet, an employee hunting data across different systems — does not scale beyond a few dozen requests; the operational answer is a privacy portal ("Privacy Center") with an automated DSAR (Data Subject Access Request) flow, since the legal DEADLINE is 15 days — without automation, that deadline systematically becomes unviable as soon as request volume grows.</p>

<h3>6. RIPD/DPIA: assess risk before processing, not after the incident</h3>
<p>The Data Protection Impact Report (RIPD in LGPD, DPIA in GDPR) is mandatory when processing involves high risk — sensitive-category data, automated decisions about people, children's data, systematic monitoring. The document describes the processing, purpose, data and data-subject categories involved, assesses necessity and proportionality, identifies risks with probability and impact, defines mitigation measures, and receives a formal DPO opinion. The logic behind the requirement is preventive: force risk assessment BEFORE processing starts, not after a leak reveals the risk was never thought through.</p>

<h3>7. Continuous compliance: apply DevOps principles to audit</h3>
<p>The problem continuous compliance solves is structural: traditional annual audit produces a snapshot of the system at ONE instant in the year, which may already be outdated the next day — and the process of collecting evidence manually (screenshots, spreadsheets, confirmation emails) consumes weeks of repetitive work and still produces a static document. The alternative applies the same infrastructure-as-code logic to compliance: each control becomes an automatically evaluable RULE ("every S3 bucket must be private"); the real environment is CONTINUOUSLY evaluated against those rules, not once a year; evidence (logs, exports, automatic screenshots) is generated by the system itself, not by a human hunting proof; and it is stored in an immutable location (WORM — Write Once Read Many). The practical result: when the auditor arrives, they QUERY the compliance platform directly, instead of waiting for the company to gather evidence under pressure — the audit stops being a traumatic multi-month event and becomes an almost-instant report of what was already being measured all year.</p>

<h3>8. The continuous-compliance tool ecosystem</h3>
<p><strong>AWS Config</strong>, <strong>Azure Policy</strong>, and <strong>GCP Organization Policies</strong> detect configuration drift in cloud resources themselves — a bucket that became public without authorization, for example, is flagged the moment the change happens, not only at the next manual audit. <strong>Cloud Custodian</strong> generalizes that idea with policy rules AND automatic remediation in YAML, working across multiple clouds at once. <strong>Drata, Vanta, Sprinto, Tugboat Logic, Secureframe</strong> are SaaS platforms specialized in collecting evidence from several sources (cloud, GitHub, identity provider, MDM, HR system) automatically and keeping a dashboard showing the real-time compliance level against a specific framework (SOC 2, ISO 27001) — the kind of tool that turned continuous compliance from an academic concept into common practice for SaaS startups. <strong>OpenSCAP</strong> validates Linux configuration against standardized SCAP benchmarks; OpenShift's <strong>Compliance Operator</strong> applies the same principle (via kube-bench and policies) inside Kubernetes clusters. <strong>OneTrust</strong> and <strong>BigID</strong> focus specifically on privacy and third-party risk management — tracking which vendors have access to what kind of data.</p>

<h3>9. AWS Config in practice: a rule becomes a continuous check</h3>
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
<p>Once enabled, that rule re-evaluates EVERY S3 bucket in the account on every configuration change, not only once — a bucket that was private and was made public at 3am appears as non-compliant at the same moment, without waiting for the next audit cycle. A "Conformance Pack" groups dozens of individual rules under the name of a specific framework (here, an LGPD baseline), allowing you to evaluate "are we compliant with X?" as a single question, instead of checking rule by rule manually.</p>

<h3>10. Evidence as code: everything the audit will ask for, generated automatically</h3>
<p>The list of what makes up automated evidence is long because it covers different areas of the system: pipeline output (lint, SAST, vulnerability scan, DAST) proves code passed the declared controls; kube-bench/kubescape output proves cluster hardening; AWS Config/Azure Policy exports prove infrastructure compliance; IAM logs (CloudTrail, GCP audit log) prove who accessed what; VPC Flow Logs prove network traffic patterns; SCA/SBOM/image-scan reports prove dependency management; approved-PR logs prove code review; LMS logs prove employee training; and MDM configuration proves laptops are encrypted and screen-locked. Storing all of that in an S3 bucket with Object Lock (which prevents alteration or deletion even by an administrator, within the retention period) is what makes the evidence TRUSTWORTHY for an auditor — data that could have been edited after the fact proves nothing. The auditor receives a pre-signed URL with an expiration, instead of direct permanent access to the environment.</p>

<h3>11. Tagging: the foundation that makes a data policy applicable</h3>
<pre><code>tags:
  data_classification: pii  # public, internal, pii, phi, pci
  retention_days: 365
  owner: team-billing
  compliance: lgpd,sox
  env: prod</code></pre>
<p>Without consistent classification on EVERY resource, a rule like "every resource with PII data must have encryption enabled, be private, and have logging active" cannot be evaluated automatically — Cloud Custodian (or equivalent) simply does not know WHICH resources that rule should check. The <code>data_classification</code> tag is what turns a policy written in text into an executable policy: the system filters by that tag and applies the check only where it matters, without depending on a human manually remembering where each type of sensitive data lives.</p>

<h3>12. Day-to-day practices that sustain continuous compliance</h3>
<p>Keeping the processing inventory updated is what makes section 3 work in practice, not only on paper. Encryption in transit and at rest EVERYWHERE — with no exception "only on this legacy system" — eliminates an entire category of leak risk. An automated DSAR portal operates section 5. Annual employee training reduces the human-error vector, historically the most common cause of data incidents. Automated retention policy (lifecycle policies that delete data after the defined period) avoids accumulating data that should no longer exist — data that does not exist cannot leak. A formal DPA (Data Processing Agreement) with each processor documents the responsibility split from section 4. Sensitive-data access monitoring (DAM — Database Activity Monitoring — and audit trails) detects internal misuse, not only external attack. And incident notification within 72 hours is a legal deadline under LGPD and GDPR — without a process already designed BEFORE the incident happens, that deadline is practically impossible to meet under the pressure of a real crisis.</p>

<h3>13. SOC 2 in detail: the five criteria and what Type II really proves</h3>
<p>The five Trust Services Criteria are <strong>Security</strong> (mandatory in any SOC 2 report — basic system-protection controls), <strong>Availability</strong> (availability SLAs met), <strong>Processing Integrity</strong> (processing produces correct and complete results), <strong>Confidentiality</strong> (data marked confidential is protected as such), and <strong>Privacy</strong> (personal-data processing, partially overlapping LGPD/GDPR). The difference between Type I and Type II is not scope, it is TIME: Type I evaluates whether controls are well DESIGNED at a point in time — it could, in theory, be satisfied by newly created controls that never actually ran. Type II evaluates whether those same controls EFFECTIVELY OPERATED over at least 6 months — that is why serious enterprise buyers demand Type II: it proves a history of real operation, not documented intention. An independent CPA auditor (not the company itself) issues the final report.</p>

<h3>14. ISO 27001: a management system, not a list of checked boxes</h3>
<p>Clauses 4 to 10 of the standard define a Management System based on the PDCA cycle (Plan-Do-Check-Act) — certification does not evaluate only isolated technical controls, it evaluates whether a continuous information-security improvement PROCESS exists. Annex A lists 93 controls organized in four groups (Organizational, People, Physical, Technological, in the 2022 version of the standard) — but not every control applies to every company, and that is where the SoA (Statement of Applicability) comes in: a formal document declaring which controls apply, which do not, and the JUSTIFICATION for each exclusion, because "we did not implement" without justification is not accepted by the auditor. Certification requires annual internal audit plus external audit to certify, with intermediate surveillance over a 3-year cycle — it is not a one-time seal, it is continuous renewal of evidence.</p>

<h3>15. Five anti-patterns that turn compliance into theater</h3>
<ul>
<li><strong>Compliance theater</strong>: written policies nobody reads, documented controls nobody actually applies, evidence fabricated in a rush for the auditor — the most expensive form of compliance, because it consumes resources without reducing any real risk.</li>
<li><strong>Once-a-year panic audit</strong>: the exact opposite of what continuous compliance (section 7) solves — if the company only discovers its own compliance state under deadline pressure, the structural problem was never fixed, only hidden between one audit and the next.</li>
<li><strong>Privacy by accident</strong>: "we'll think about LGPD later" guarantees expensive rework — redesigning a system to add privacy after the fact is orders of magnitude more expensive than designing it right from the start (privacy by design).</li>
<li><strong>DPO without real authority</strong>: a role created only to appear on the org chart, without power to block a launch or demand a fix, does not fulfill the function the law assumes for the role.</li>
<li><strong>Processor without a DPA</strong>: the company remains legally responsible for data a vendor processes on its behalf — without a formal contract documenting that relationship, there is no way to demonstrate diligence in an inspection.</li>
</ul>

<h3>16. Pragmatic roadmap: where to start when none of this exists yet</h3>
<ol>
<li>Identify the priority framework — a large B2B customer demanding SOC 2 changes priority differently from "we only serve the Brazilian market, LGPD is the non-negotiable minimum".</li>
<li>Do a gap analysis: where the environment is today versus where the chosen framework requires it to be.</li>
<li>Implement fundamental controls first — encryption, MFA, RBAC, audit log, backup — the baseline practically every framework requires, before any more specific control.</li>
<li>Classify and tag data with consistent tags (section 11), a prerequisite for any automated policy to work.</li>
<li>Adopt a continuous-compliance tool sized to the company — Drata/Vanta for SaaS, AWS Config for pure infrastructure.</li>
<li>Formalize a DPA with every vendor that processes data on your behalf.</li>
<li>Build the privacy portal to operationalize data-subject rights without a manual process.</li>
<li>Run an internal audit before hiring the external one — finding your own gaps is cheaper than the external auditor finding them first.</li>
<li>Advance from Type I to Type II (or equivalent) as operation history accumulates — Type II is not reachable on day one, it requires real operation time.</li>
</ol>
"""
                ),
                "practical": (
                    "Configure AWS Config Rules: <code>s3-bucket-public-read-prohibited</code>, "
                    "<code>encrypted-volumes</code>, <code>iam-password-policy</code>, "
                    "<code>vpc-flow-logs-enabled</code>. Crie um Conformance Pack que agrupe "
                    "10+ regras alinhadas com LGPD. Configure entrega de relatório semanal em "
                    "bucket S3 com Object Lock. Teste violando uma regra (criando bucket público) "
                    "e veja AWS Config marcar como NON_COMPLIANT em minutos."
                ),
                "practical_en": (
                    "Configure AWS Config Rules: <code>s3-bucket-public-read-prohibited</code>, "
                    "<code>encrypted-volumes</code>, <code>iam-password-policy</code>, "
                    "<code>vpc-flow-logs-enabled</code>. Create a Conformance Pack grouping 10+ rules aligned "
                    "with LGPD. Configure weekly report delivery to an S3 bucket with Object Lock. Test by "
                    "violating a rule (creating a public bucket) and watch AWS Config mark it NON_COMPLIANT "
                    "within minutes."
                ),
            },
            "materials": [
                m("LGPD (texto da lei)", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", "docs", "", title_en="LGPD (law text)", description_en=""),
                m("ISO 27001 overview", "https://www.iso.org/isoiec-27001-information-security.html", "docs", "", title_en="ISO 27001 overview", description_en=""),
                m("AWS Config", "https://docs.aws.amazon.com/config/latest/developerguide/", "docs", "", title_en="AWS Config", description_en=""),
                m("OpenSCAP", "https://www.open-scap.org/", "tool", "", title_en="OpenSCAP", description_en=""),
                m("Cloud Custodian", "https://cloudcustodian.io/", "tool", "", title_en="Cloud Custodian", description_en=""),
                m("ANPD (autoridade BR)", "https://www.gov.br/anpd/pt-br", "docs", "", title_en="ANPD (BR authority)", description_en=""),
                m("SOC 2 overview (AICPA)", "https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2", "docs", "", title_en="SOC 2 overview (AICPA)", description_en=""),
                m("Drata vs Vanta vs Secureframe (G2)", "https://www.g2.com/categories/security-compliance", "article", "Comparação de continuous compliance SaaS.", title_en="Drata vs Vanta vs Secureframe (G2)", description_en="Comparison of continuous compliance SaaS."),
            ],
            "questions": [
                q("LGPD aplica-se a:",
                  "Tratamento de dados pessoais no Brasil.",
                  ["Só o tratamento de dados que já são públicos.", "Só empresas brasileiras que exportam para fora do país.", "Só o tratamento de dados pessoais de menores de idade."],
                  "Aplica também a empresas estrangeiras que tratam dados de pessoas no Brasil.",
                  statement_en="LGPD applies to:",
                  correct_en="Processing of personal data in Brazil.",
                  wrong_en=["Only the processing of data that is already public.", "Only Brazilian companies that export abroad.", "Only the processing of personal data of minors."],
                  explanation_en="It also applies to foreign companies that process data of people in Brazil."),
                q("Princípio de minimização:",
                  "Coletar apenas os dados necessários para a finalidade.",
                  ["Coletar o máximo de dado possível sobre o usuário.", "Manter os dados guardados pelo maior tempo possível.", "Compartilhar os dados coletados com qualquer parceiro."],
                  "Pergunta-chave: 'preciso desse dado para a finalidade declarada?'.",
                  statement_en="Minimization principle:",
                  correct_en="Collect only the data needed for the purpose.",
                  wrong_en=["Collect as much data as possible about the user.", "Keep the data stored for as long as possible.", "Share the collected data with any partner."],
                  explanation_en="Key question: 'do I need this data for the declared purpose?'."),
                q("DPIA / RIPD:",
                  "Avaliação de impacto à proteção de dados.",
                  ["Um tipo específico de configuração de TLS.", "Um mecanismo de backup dos dados da aplicação.", "Um conjunto de registros relacionados a DNS."],
                  "Obrigatório quando tratamento envolve risco alto. Avalia probabilidade e impacto.",
                  statement_en="DPIA / RIPD:",
                  correct_en="A data-protection impact assessment.",
                  wrong_en=["A specific type of TLS configuration.", "A backup mechanism for application data.", "A set of records related to DNS."],
                  explanation_en="Mandatory when processing involves high risk. Assesses probability and impact."),
                q("ISO 27001 é:",
                  "Norma para sistema de gestão de segurança da informação.",
                  ["Um provedor específico de serviços em nuvem, suposição incorreta sobre como o sistema realmente se comporta sob estresse.", "Um tipo específico de algoritmo de criptografia, atalho que ignora exatamente o cenário que mais importa evitar.", "Um servidor responsável pela resolução de DNS, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto."],
                  "Foco em SGSI. Anexo A lista 93 controles. Certificação anual.",
                  statement_en="ISO 27001 is:",
                  correct_en="A standard for an information security management system.",
                  wrong_en=["A specific cloud service provider, an incorrect assumption about how the system actually behaves under stress.", "A specific type of encryption algorithm, a shortcut that skips exactly the scenario most worth avoiding.", "A server responsible for DNS resolution, a decision that looks reasonable in isolation but breaks the architecture as a whole."],
                  explanation_en="Focus on ISMS. Annex A lists 93 controls. Annual certification."),
                q("SOC 2 Type II:",
                  "Atesta operação dos controles em um período (ex.: 6 meses).",
                  ["Uma etapa considerada relevante só na fase de design, comportamento que confunde quem está debugando meses depois.", "Um selo usado só para fins de marketing da empresa, prática que só aparece como erro grave durante um incidente real.", "Uma certificação relevante só dentro do escopo do PCI, prática que gera falso senso de segurança no time."],
                  "Type I é design pontual; Type II é mais valorizado por mostrar consistência.",
                  statement_en="SOC 2 Type II:",
                  correct_en="Attests control operation over a period (e.g. 6 months).",
                  wrong_en=["A stage considered relevant only in the design phase, behavior that confuses whoever is debugging months later.", "A seal used only for company marketing purposes, a practice that only shows up as a serious error during a real incident.", "A certification relevant only within the PCI scope, a practice that creates a false sense of security on the team."],
                  explanation_en="Type I is point-in-time design; Type II is more valued for showing consistency."),
                q("Continuous compliance:",
                  "Detecção automática contínua de desvios.",
                  ["Uma planilha de checklist preenchida manualmente.", "Uma auditoria única, feita uma vez por ano.", "Ignorar o assunto até a chegada de um auditor."],
                  "AWS Config, Drata, Vanta, alertam quando configuração sai do padrão.",
                  statement_en="Continuous compliance:",
                  correct_en="Continuous automatic detection of drift.",
                  wrong_en=["A checklist spreadsheet filled in manually.", "A single audit, done once a year.", "Ignoring the topic until an auditor arrives."],
                  explanation_en="AWS Config, Drata, Vanta alert when configuration leaves the standard."),
                q("Evidências como código:",
                  "Geração automatizada e armazenamento auditável.",
                  ["Um documento impresso em PDF guardado numa pasta.", "Um comprovante enviado avulso por e-mail.", "Uma captura de tela guardada localmente pelo analista."],
                  "Pipeline gera; bucket WORM guarda. Auditor consulta e verifica.",
                  statement_en="Evidence as code:",
                  correct_en="Automated generation and auditable storage.",
                  wrong_en=["A PDF document printed and kept in a folder.", "A receipt sent ad hoc by email.", "A screenshot stored locally by the analyst."],
                  explanation_en="Pipeline generates; WORM bucket stores. Auditor queries and verifies."),
                q("DPO é:",
                  "Encarregado de proteção de dados.",
                  ["Um cargo genérico dentro da área de TI da empresa.", "Uma função que só existe dentro do escopo do PCI.", "Um título informal sem responsabilidade formal definida."],
                  "Função obrigatória na LGPD. Pode ser interno ou externo.",
                  statement_en="A DPO is:",
                  correct_en="A data protection officer.",
                  wrong_en=["A generic role within the company's IT area.", "A function that only exists within the PCI scope.", "An informal title with no formal responsibility defined."],
                  explanation_en="Mandatory role under LGPD. Can be internal or external."),
                q("PCI DSS aplica-se a:",
                  "Empresas que lidam com dados de cartão de pagamento.",
                  ["Só empresas que operam exclusivamente como SaaS, suposição que vale só até o primeiro imprevisto de rede ou hardware.", "Qualquer e-commerce, mesmo sem processar cartões, que só aparece como problema depois que o sistema já está em produção.", "Só instituições bancárias tradicionais, erro típico de configuração feita às pressas, sem revisão posterior."],
                  "Mesmo que você use Stripe, há controles de escopo. PCI tem 12 requisitos amplos.",
                  statement_en="PCI DSS applies to:",
                  correct_en="Companies that handle payment-card data.",
                  wrong_en=["Only companies that operate exclusively as SaaS, an assumption that holds only until the first network or hardware surprise.", "Any e-commerce, even without processing cards, which only shows up as a problem after the system is already in production.", "Only traditional banking institutions, a typical mistake from configuration done in a rush without later review."],
                  explanation_en="Even if you use Stripe, there are scope controls. PCI has 12 broad requirements."),
                q("Cloud Custodian:",
                  "Engine de policy para detectar e remediar em cloud.",
                  ["Um substituto direto e completo do próprio Kubernetes.", "Um mecanismo de backup dos recursos da conta.", "Um ambiente de desenvolvimento integrado (IDE)."],
                  "Policy YAML: filtra recursos + ação (notify/tag/stop/delete). Open source.",
                  statement_en="Cloud Custodian:",
                  correct_en="A policy engine to detect and remediate in the cloud.",
                  wrong_en=["A direct and complete substitute for Kubernetes itself.", "A backup mechanism for account resources.", "An integrated development environment (IDE)."],
                  explanation_en="YAML policy: filter resources + action (notify/tag/stop/delete). Open source."),
            ],
        },
    ],
}
