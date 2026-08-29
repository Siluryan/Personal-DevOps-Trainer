"""Fase 2, Introdução à Nuvem (Cloud Essentials)."""
from ._helpers import m, q

PHASE2 = {
    "name": "Fase 2: Introdução à Nuvem (Cloud Essentials)",
    "name_en": "Phase 2: Introduction to the Cloud (Cloud Essentials)",
    "description": "Saindo do servidor físico/local para recursos sob demanda.",
    "description_en": "Moving from physical/local servers to on-demand resources.",
    "topics": [
        # =====================================================================
        # 2.1 Virtualização vs. Cloud
        # =====================================================================
        {
            "title": "Virtualização vs. Cloud",
            "title_en": "Virtualization vs. Cloud",
            "summary": "Como a nuvem abstrai o hardware e o que muda em relação a VMs tradicionais.",
            "summary_en": "How the cloud abstracts hardware and what changes compared to traditional VMs.",
            "lesson": {
                "intro": (
                    "Cloud não é simplesmente 'computador de outra pessoa'. É virtualização "
                    "+ APIs + multi-tenancy + cobrança por consumo + serviços gerenciados + "
                    "automação radical. Confundir cloud com 'datacenter alugado' leva a "
                    "decisões caras: arquiteturas que não escalam, faturas três vezes maiores "
                    "que o esperado, lock-in mal calculado.<br><br>"
                    "Esta aula é um modelo mental sólido sobre as camadas técnicas que "
                    "compõem o que chamamos de cloud, desde o hypervisor no host até a "
                    "diferença real entre IaaS, PaaS e SaaS, passando por trade-offs e "
                    "padrões de arquitetura. É o vocabulário comum a tudo que vem nas "
                    "próximas aulas."
                ),
                "intro_en": (
                    "Cloud isn't simply 'someone else's computer'. It's virtualization "
                    "+ APIs + multi-tenancy + consumption-based billing + managed services + "
                    "radical automation. Confusing cloud with a 'rented datacenter' leads to "
                    "expensive decisions: architectures that don't scale, bills three times "
                    "higher than expected, badly miscalculated lock-in.<br><br>"
                    "This lesson builds a solid mental model of the technical layers "
                    "that make up what we call cloud, from the hypervisor on the host to the "
                    "real difference between IaaS, PaaS, and SaaS, covering trade-offs and "
                    "architecture patterns along the way. It's the shared vocabulary for "
                    "everything in the upcoming lessons."
                ),
                "body": (
                """<h3>1. Da máquina física à VM: hypervisor</h3>
<p>Antes de cloud existir, cada workload ocupava um servidor físico
inteiro, e a utilização típica desses servidores girava em torno de
apenas 10-15% da capacidade real — a maior parte do hardware ficava
ociosa a maior parte do tempo. O <strong>hypervisor</strong> resolve
exatamente esse desperdício: é o software que cria múltiplas máquinas
virtuais compartilhando o mesmo hardware físico. O tipo 1
(<strong>bare-metal</strong>) roda direto sobre o hardware, com acesso
privilegiado às extensões de virtualização da própria CPU (Intel VT-x,
AMD-V) — KVM (Linux), VMware ESXi, Microsoft Hyper-V, Xen e o AWS Nitro
Hypervisor (uma bifurcação customizada do KVM) seguem esse modelo, e é
exatamente o que toda cloud pública usa por trás dos panos. O tipo 2
(<strong>hosted</strong>) roda como uma aplicação comum dentro de um
sistema operacional já existente — VirtualBox, VMware Workstation,
Parallels — útil em desktop, mas ineficiente demais para servidor de
produção. Cada VM carrega seu próprio kernel, drivers virtualizados
(paravirtualização via <code>virtio</code>) e endereço IP próprio — o
que permite rodar Windows, Linux e BSD lado a lado, isolados, no mesmo
host físico.</p>
<div class="mermaid">
flowchart TD
    subgraph VM ["Máquina virtual"]
        H1["Hardware físico"] --> HV["Hypervisor"]
        HV --> G1["SO convidado 1"] --> A1["App"]
        HV --> G2["SO convidado 2"] --> A2["App"]
    end
    subgraph CT ["Container"]
        H2["Hardware físico"] --> SO["SO único, kernel compartilhado"]
        SO --> C1["Container 1"] --> B1["App"]
        SO --> C2["Container 2"] --> B2["App"]
    end
</div>


<h3>2. Container ≠ VM</h3>
<table>
<tr><th></th><th>VM</th><th>Container</th></tr>
<tr><td>Kernel</td><td>próprio</td><td>compartilhado com host</td></tr>
<tr><td>Boot</td><td>segundos a minutos</td><td>milissegundos</td></tr>
<tr><td>Tamanho</td><td>GBs</td><td>dezenas a centenas de MB</td></tr>
<tr><td>Isolamento</td><td>forte (boundary do hypervisor)</td>
<td>processo (namespaces + cgroups + seccomp)</td></tr>
<tr><td>SO no guest</td><td>qualquer</td><td>mesmo kernel do host</td></tr>
</table>
<p>A diferença fundamental é que um container é um PROCESSO isolado,
não uma máquina separada — e é exatamente por isso que ele inicia em
milissegundos em vez de minutos. Em Linux, essa ilusão de isolamento
vem de três mecanismos do próprio kernel: <strong>namespaces</strong>
isolam a VISÃO que cada container tem de PID, mount, rede, IPC, user e
UTS — cada um "enxerga" só o próprio mundo, mesmo compartilhando o
mesmo kernel físico; <strong>cgroups</strong> limitam quanto de CPU,
RAM e I/O cada container pode consumir do host; e
<strong>seccomp/AppArmor/SELinux</strong> restringem quais syscalls o
processo dentro do container tem permissão de chamar. Para um
isolamento mais forte que container puro, mas ainda muito mais leve
que uma VM completa, <strong>microVMs</strong> (Firecracker da AWS,
Kata Containers) rodam um kernel mínimo dentro do próprio KVM,
inicializando em centenas de milissegundos.</p>

<h3>3. O que cloud adiciona sobre virtualização</h3>
<p>Virtualização sozinha já existia décadas antes da cloud pública —
o que a cloud acrescenta é uma camada inteira de automação por cima.
API em tudo significa provisionar VM, rede, storage ou banco via uma
chamada HTTP autenticada — no VMware tradicional você abria um ticket
para um time de infraestrutura, na AWS você roda <code>aws ec2
run-instances</code> e recebe o recurso em segundos. Pay-as-you-go
cobra por hora, segundo, milissegundo (no caso do Lambda) ou byte
(no caso do S3) — capex vira opex, sem investimento inicial em
hardware. Multi-tenancy coloca muitos clientes diferentes na mesma
infraestrutura física, isolados apenas por software, o que é o que
torna o preço por unidade tão mais baixo do que hardware dedicado.
Serviços gerenciados (RDS, Cloud SQL, DynamoDB, EKS) cobram uma camada
inteira acima da VM crua, tirando de você a operação do banco ou do
cluster em si. Geo-distribuição oferece dezenas de regiões, dezenas de
AZs por região, e edge em praticamente todo o mundo. E composição via
IaC (Terraform, CloudFormation, Pulumi) permite descrever a
infraestrutura inteira como texto versionado, revisável e
reproduzível — o assunto central da Fase 3.</p>

<h3>4. IaaS vs PaaS vs SaaS, o trade-off de controle</h3>
<table>
<tr><th></th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>
<tr><td>Você controla</td><td>SO, runtime, app, dados</td>
<td>app, dados</td><td>config, dados</td></tr>
<tr><td>Provedor controla</td><td>hardware, hypervisor</td>
<td>hardware, hypervisor, SO, runtime</td><td>tudo</td></tr>
<tr><td>Exemplos</td><td>EC2, GCE, Azure VM</td>
<td>App Engine, Heroku, Cloud Run, App Service</td>
<td>Gmail, Notion, GitHub, Salesforce</td></tr>
<tr><td>Esforço operacional</td><td>alto</td><td>médio</td><td>quase zero</td></tr>
<tr><td>Lock-in</td><td>baixo</td><td>alto</td><td>muito alto</td></tr>
<tr><td>Granularidade</td><td>total</td><td>limitada</td><td>nenhuma</td></tr>
</table>
<p>A diferença central entre as três camadas é literalmente QUEM opera
cada parte da pilha — quanto mais o provedor assume, menos esforço
operacional sobra para você, mas também menos controle e mais lock-in.
Duas tendências recentes ficam num meio-termo deliberado:
<strong>serverless</strong> (Lambda, Cloud Functions, Cloud Run) e
<strong>containers as a service</strong> (Fargate, Cloud Run) — você
entrega uma imagem ou uma função, e o provedor cuida de tudo entre isso
e o hardware, sem virar PaaS completo nem exigir gerenciar servidor.</p>

<h3>5. Anatomia de uma região AWS (e equivalentes)</h3>
<pre><code>Region (ex.: us-east-1, sa-east-1, eu-west-3)
├── AZ a (datacenter A)        ← latência ~1-2ms intra-AZ
├── AZ b (datacenter B)        ← latência ~1-2ms intra-AZ
└── AZ c (datacenter C)        ← latência ~1-2ms entre-AZ
    │
    └── Edges (POPs / CloudFront / Global Accelerator)
         espalhados por dezenas de cidades</code></pre>
<p>Uma <strong>Region</strong> é um conjunto de datacenters numa
localidade geográfica específica — us-east-1, por exemplo, fica no
norte da Virgínia. Uma <strong>Availability Zone</strong> (AZ) é um ou
mais datacenters isolados entre si em energia, refrigeração e rede — a
falha de uma AZ, em tese, não deveria afetar as outras dentro da mesma
região. E um <strong>Edge/POP</strong> é um ponto de presença dedicado
a CDN e aceleração — não roda a aplicação inteira, mas cacheia conteúdo
fisicamente perto do usuário final. Alta disponibilidade básica
significa multi-AZ; alta disponibilidade séria significa multi-region,
com replicação ativa-ativa ou ativa-passiva — muito mais caro e
complexo, e só faz sentido ativar se o SLA contratado realmente
exigir esse nível.</p>

<h3>6. Os 'Big 3' e os outros</h3>
<table>
<tr><th></th><th>AWS</th><th>Azure</th><th>GCP</th></tr>
<tr><td>Computação</td><td>EC2</td><td>VM</td><td>Compute Engine</td></tr>
<tr><td>Container managed</td><td>EKS / Fargate</td>
<td>AKS / Container Apps</td><td>GKE / Cloud Run</td></tr>
<tr><td>Object Storage</td><td>S3</td><td>Blob Storage</td><td>GCS</td></tr>
<tr><td>SQL gerenciado</td><td>RDS</td><td>Azure SQL / DB</td>
<td>Cloud SQL / AlloyDB</td></tr>
<tr><td>NoSQL</td><td>DynamoDB</td><td>Cosmos DB</td><td>Bigtable / Firestore</td></tr>
<tr><td>Serverless function</td><td>Lambda</td>
<td>Functions</td><td>Cloud Functions / Run</td></tr>
<tr><td>Identidade</td><td>IAM</td><td>Entra ID</td><td>IAM</td></tr>
<tr><td>Rede</td><td>VPC</td><td>VNet</td><td>VPC</td></tr>
</table>
<p>Fora dos três grandes, várias alternativas atendem nicho
específico: DigitalOcean é conhecida por experiência amigável a
desenvolvedor; Linode/Akamai e Hetzner competem em preço, especialmente
Hetzner na Europa; a Oracle Cloud oferece um free tier
particularmente generoso; Cloudflare aposta tudo em edge-first; e o
Fly.io foca em deploy de container distribuído globalmente com pouco
esforço de configuração.</p>

<h3>7. Tipos de cloud: pública, privada, híbrida, edge</h3>
<p>A cloud <strong>pública</strong> (AWS, Azure, GCP) é compartilhada
entre clientes, e por isso oferece a maior elasticidade e o melhor
preço por terabyte. A cloud <strong>privada</strong> — datacenter
próprio com VMware ou OpenStack, ou uma VPC/instância dedicada num
provedor público — garante isolamento exigido por regulação legal, ao
custo de perder boa parte da elasticidade que torna a nuvem pública
atraente. O modelo <strong>híbrido</strong> combina os dois via VPN,
Direct Connect ou Outposts, útil especificamente durante transição
gradual ou quando um dado específico não PODE sair do país (LGPD,
questões de soberania de dado). O modelo <strong>edge</strong> — como
Cloudflare Workers, AWS Lambda@Edge, Fastly Compute@Edge — coloca
computação fisicamente perto do usuário final, entregando latência
abaixo de 50ms em escala global. E <strong>multi-cloud</strong> —
vários provedores ao mesmo tempo — teve seu momento de hype, mas a
complexidade operacional real de manter consistência entre provedores
diferentes se mostrou alta o bastante para esfriar bastante o
entusiasmo inicial.</p>

<h3>8. Trade-offs reais que ninguém explica no marketing</h3>
<p>Cinco trade-offs raramente aparecem no material promocional de
qualquer provedor. Egress é caro de verdade: a AWS cobra cerca de 9
centavos de dólar por GB de tráfego saindo — uma aplicação que serve
muito vídeo paga uma fortuna nessa única linha, o que abriu espaço para
alternativas como Cloudflare R2 competirem diretamente zerando esse
custo. Lock-in é real, não FUD de concorrente: adotar DynamoDB ou
BigQuery "até o fim" significa que migrar depois é literalmente um
projeto de meses — vale perguntar "como eu saio disso?" ANTES de
adotar um serviço gerenciado proprietário, não depois. Falha acontece
mesmo na infraestrutura mais madura: us-east-1 já ficou fora do ar por
horas em mais de uma ocasião (2017, 2021, 2023) — multi-region deixa de
ser luxo em qualquer sistema realmente crítico. Latência entre AZ
distante importa: cerca de 1-2ms dentro da mesma AZ contra 10-100ms
entre regiões diferentes, o suficiente para degradar performance de
banco de dados se a arquitetura não considerar isso desde o início. E
FinOps fica caro sem disciplina: depois de seis meses, uma conta com
milhares de recursos órfãos esquecidos rodando silenciosamente se torna
o padrão, não a exceção.</p>

<h3>9. Caso real: o jornalista que ganhou um datacenter</h3>
<p>Em 2017, um jornalista holandês colocou um site novo na AWS
(S3 + CloudFront), esperando um custo de hospedagem em torno de US$ 5
por mês para cerca de 10 mil visitantes por dia. Um bug de loop
esqueceu de aplicar rate-limit num write para o DynamoDB, e o sistema
passou a fazer milhões de escritas por minuto sem nenhum limite
contendo isso. Em 24 horas, a fatura chegou a US$ 14 mil. As lições
ficam diretas: configurar budget e alerta ANTES do primeiro deploy,
nunca depois; aplicar rate-limit em TUDO que aceita escrita repetida; e
preferir soft-delete a um loop de write que pode escapar de controle
silenciosamente.</p>

<h3>10. Quando cloud não é a resposta</h3>
<p>Quatro cenários específicos ainda favorecem infraestrutura
on-premise sobre cloud: workload com utilização constante e previsível
(um banco de dados sempre no limite da capacidade), onde comprar o
hardware uma vez sai mais barato em três anos do que pagar por
elasticidade que nunca é usada; dado que não pode sair do país por
regulação específica; latência ultra-baixa que a distância física até
o datacenter da cloud simplesmente não permite (trading de alta
frequência, por exemplo); e carga com I/O de armazenamento massivo,
onde a cloud cobra caro justamente por IOPS. Para praticamente todo o
resto — startup nova, aplicação web típica, batch de machine learning,
site ou blog — cloud continua sendo a escolha mais óbvia na maioria dos
casos.</p>"""
                ),
                "body_en": (
                """<h3>1. From physical machine to VM: the hypervisor</h3>
<p>Before cloud existed, each workload occupied an entire physical
server, and typical utilization of those servers hovered around
only 10-15% of real capacity — most of the hardware sat
idle most of the time. The <strong>hypervisor</strong> solves
exactly that waste: it's the software that creates multiple virtual
machines sharing the same physical hardware. Type 1
(<strong>bare-metal</strong>) runs directly on the hardware, with
privileged access to the CPU's own virtualization extensions (Intel VT-x,
AMD-V) — KVM (Linux), VMware ESXi, Microsoft Hyper-V, Xen, and the AWS Nitro
Hypervisor (a customized fork of KVM) follow this model, and it's
exactly what every public cloud uses behind the scenes. Type 2
(<strong>hosted</strong>) runs as a regular application inside an
already-existing operating system — VirtualBox, VMware Workstation,
Parallels — useful on desktop, but too inefficient for a production
server. Each VM carries its own kernel, virtualized drivers
(paravirtualization via <code>virtio</code>), and its own IP address — which
allows Windows, Linux, and BSD to run side by side, isolated, on the same
physical host.</p>
<div class="mermaid">
flowchart TD
    subgraph VM ["Máquina virtual"]
        H1["Hardware físico"] --> HV["Hypervisor"]
        HV --> G1["SO convidado 1"] --> A1["App"]
        HV --> G2["SO convidado 2"] --> A2["App"]
    end
    subgraph CT ["Container"]
        H2["Hardware físico"] --> SO["SO único, kernel compartilhado"]
        SO --> C1["Container 1"] --> B1["App"]
        SO --> C2["Container 2"] --> B2["App"]
    end
</div>


<h3>2. Container ≠ VM</h3>
<table>
<tr><th></th><th>VM</th><th>Container</th></tr>
<tr><td>Kernel</td><td>own</td><td>shared with host</td></tr>
<tr><td>Boot</td><td>seconds to minutes</td><td>milliseconds</td></tr>
<tr><td>Size</td><td>GBs</td><td>tens to hundreds of MB</td></tr>
<tr><td>Isolation</td><td>strong (hypervisor boundary)</td>
<td>process-level (namespaces + cgroups + seccomp)</td></tr>
<tr><td>Guest OS</td><td>any</td><td>same kernel as host</td></tr>
</table>
<p>The fundamental difference is that a container is an isolated PROCESS,
not a separate machine — and that's exactly why it starts in
milliseconds instead of minutes. On Linux, that illusion of isolation
comes from three kernel mechanisms: <strong>namespaces</strong>
isolate the VIEW each container has of PID, mount, network, IPC, user, and
UTS — each one "sees" only its own world, even while sharing the
same physical kernel; <strong>cgroups</strong> limit how much CPU,
RAM, and I/O each container can consume from the host; and
<strong>seccomp/AppArmor/SELinux</strong> restrict which syscalls the
process inside the container is allowed to call. For stronger
isolation than a plain container, but still much lighter
than a full VM, <strong>microVMs</strong> (AWS's Firecracker,
Kata Containers) run a minimal kernel inside KVM itself,
booting in hundreds of milliseconds.</p>

<h3>3. What cloud adds on top of virtualization</h3>
<p>Virtualization alone existed decades before public cloud —
what cloud adds is an entire layer of automation on top.
APIs everywhere means provisioning a VM, network, storage, or database via a
single authenticated HTTP call — with traditional VMware you'd open a ticket
to an infrastructure team, on AWS you run <code>aws ec2
run-instances</code> and get the resource in seconds. Pay-as-you-go
charges by the hour, second, millisecond (in Lambda's case), or byte
(in S3's case) — capex becomes opex, with no upfront
hardware investment. Multi-tenancy places many different customers on the
same physical infrastructure, isolated only by software, which is
exactly what makes the per-unit price so much lower than dedicated hardware.
Managed services (RDS, Cloud SQL, DynamoDB, EKS) charge for an
entire layer above the raw VM, taking database or
cluster operations off your plate. Geo-distribution offers dozens of
regions, dozens of AZs per region, and edge presence in practically the whole
world. And composing infrastructure via
IaC (Terraform, CloudFormation, Pulumi) lets you describe the entire
infrastructure as versioned, reviewable, and
reproducible text — the central topic of Phase 3.</p>

<h3>4. IaaS vs PaaS vs SaaS, the control trade-off</h3>
<table>
<tr><th></th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>
<tr><td>You control</td><td>OS, runtime, app, data</td>
<td>app, data</td><td>config, data</td></tr>
<tr><td>Provider controls</td><td>hardware, hypervisor</td>
<td>hardware, hypervisor, OS, runtime</td><td>everything</td></tr>
<tr><td>Examples</td><td>EC2, GCE, Azure VM</td>
<td>App Engine, Heroku, Cloud Run, App Service</td>
<td>Gmail, Notion, GitHub, Salesforce</td></tr>
<tr><td>Operational effort</td><td>high</td><td>medium</td><td>near zero</td></tr>
<tr><td>Lock-in</td><td>low</td><td>high</td><td>very high</td></tr>
<tr><td>Granularity</td><td>total</td><td>limited</td><td>none</td></tr>
</table>
<p>The core difference between the three layers is literally WHO operates
each part of the stack — the more the provider takes on, the less operational
effort is left for you, but also the less control and the more lock-in.
Two recent trends sit in a deliberate middle ground:
<strong>serverless</strong> (Lambda, Cloud Functions, Cloud Run) and
<strong>containers as a service</strong> (Fargate, Cloud Run) — you
hand over an image or a function, and the provider handles everything between
that and the hardware, without becoming full PaaS or requiring you to
manage a server.</p>

<h3>5. Anatomy of an AWS region (and equivalents)</h3>
<pre><code>Region (ex.: us-east-1, sa-east-1, eu-west-3)
├── AZ a (datacenter A)        ← latência ~1-2ms intra-AZ
├── AZ b (datacenter B)        ← latência ~1-2ms intra-AZ
└── AZ c (datacenter C)        ← latência ~1-2ms entre-AZ
    │
    └── Edges (POPs / CloudFront / Global Accelerator)
         espalhados por dezenas de cidades</code></pre>
<p>A <strong>Region</strong> is a set of datacenters in a
specific geographic location — us-east-1, for example, is in
northern Virginia. An <strong>Availability Zone</strong> (AZ) is one or
more datacenters isolated from each other in power, cooling, and network — the
failure of one AZ, in theory, shouldn't affect the others within the same
region. And an <strong>Edge/POP</strong> is a point of presence dedicated
to CDN and acceleration — it doesn't run the whole application, but caches content
physically close to the end user. Basic high availability
means multi-AZ; serious high availability means multi-region,
with active-active or active-passive replication — much more expensive and
complex, and only worth turning on if the contracted SLA truly
demands that level.</p>

<h3>6. The 'Big 3' and the rest</h3>
<table>
<tr><th></th><th>AWS</th><th>Azure</th><th>GCP</th></tr>
<tr><td>Compute</td><td>EC2</td><td>VM</td><td>Compute Engine</td></tr>
<tr><td>Managed container</td><td>EKS / Fargate</td>
<td>AKS / Container Apps</td><td>GKE / Cloud Run</td></tr>
<tr><td>Object Storage</td><td>S3</td><td>Blob Storage</td><td>GCS</td></tr>
<tr><td>Managed SQL</td><td>RDS</td><td>Azure SQL / DB</td>
<td>Cloud SQL / AlloyDB</td></tr>
<tr><td>NoSQL</td><td>DynamoDB</td><td>Cosmos DB</td><td>Bigtable / Firestore</td></tr>
<tr><td>Serverless function</td><td>Lambda</td>
<td>Functions</td><td>Cloud Functions / Run</td></tr>
<tr><td>Identity</td><td>IAM</td><td>Entra ID</td><td>IAM</td></tr>
<tr><td>Network</td><td>VPC</td><td>VNet</td><td>VPC</td></tr>
</table>
<p>Outside the big three, several alternatives serve a
specific niche: DigitalOcean is known for a developer-friendly
experience; Linode/Akamai and Hetzner compete on price, especially
Hetzner in Europe; Oracle Cloud offers a particularly
generous free tier; Cloudflare bets everything on edge-first; and
Fly.io focuses on deploying containers globally distributed with little
configuration effort.</p>

<h3>7. Types of cloud: public, private, hybrid, edge</h3>
<p><strong>Public</strong> cloud (AWS, Azure, GCP) is shared
across customers, and that's why it offers the greatest elasticity and the best
price per terabyte. <strong>Private</strong> cloud — your own
datacenter with VMware or OpenStack, or a dedicated VPC/instance in a
public provider — guarantees the isolation required by legal regulation, at the
cost of losing much of the elasticity that makes public cloud
attractive. The <strong>hybrid</strong> model combines both via VPN,
Direct Connect, or Outposts, useful specifically during a gradual
transition or when a specific piece of data CANNOT leave the country (LGPD,
data sovereignty concerns). The <strong>edge</strong> model — like
Cloudflare Workers, AWS Lambda@Edge, Fastly Compute@Edge — places
computation physically close to the end user, delivering latency
below 50ms at global scale. And <strong>multi-cloud</strong> —
several providers at once — had its moment of hype, but the
real operational complexity of maintaining consistency across different
providers proved high enough to cool off most of the
initial enthusiasm.</p>

<h3>8. Real trade-offs nobody explains in the marketing</h3>
<p>Five trade-offs rarely show up in any provider's promotional
material. Egress is genuinely expensive: AWS charges around 9
cents per GB of outgoing traffic — an application that serves
a lot of video pays a fortune on that single line item, which opened space for
alternatives like Cloudflare R2 to compete directly by zeroing out that
cost. Lock-in is real, not competitor FUD: adopting DynamoDB or
BigQuery "all the way" means migrating away later is literally a
months-long project — it's worth asking "how do I get out of this?" BEFORE
adopting a proprietary managed service, not after. Failure happens
even in the most mature infrastructure: us-east-1 has already gone down for
hours on more than one occasion (2017, 2021, 2023) — multi-region stops
being a luxury in any genuinely critical system. Latency between distant
AZs matters: about 1-2ms within the same AZ versus 10-100ms
between different regions, enough to degrade database
performance if the architecture doesn't account for it from the start. And
FinOps gets expensive without discipline: after six months, an account with
thousands of orphaned resources silently running becomes
the norm, not the exception.</p>

<h3>9. Real case: the journalist who won a datacenter</h3>
<p>In 2017, a Dutch journalist put a new site on AWS
(S3 + CloudFront), expecting a hosting cost around US$5
per month for about 10 thousand daily visitors. A loop
bug forgot to apply rate-limiting on a write to DynamoDB, and the system
started making millions of writes per minute with no limit at all
holding it back. In 24 hours, the bill reached US$14
thousand. The lessons are direct: set up budget and alerts BEFORE
the first deploy, never after; apply rate-limiting on EVERYTHING that accepts
repeated writes; and prefer soft-delete over a write loop that can spiral
out of control silently.</p>

<h3>10. When cloud isn't the answer</h3>
<p>Four specific scenarios still favor on-premise
infrastructure over cloud: workloads with constant, predictable
utilization (a database always at capacity limit), where buying the
hardware once is cheaper over three years than paying for
elasticity that's never used; data that legally cannot leave the country under
specific regulation; ultra-low latency that the physical distance to
the cloud datacenter simply doesn't allow (high-frequency
trading, for example); and workloads with massive storage I/O,
where cloud charges heavily precisely for IOPS. For practically everything
else — a new startup, a typical web application, a machine-learning batch job,
a site or blog — cloud remains the more obvious choice in most
cases.</p>"""
                ),
                "practical": (
                    "(1) Crie uma conta AWS free tier (ou GCP / Azure equivalente).<br>"
                    "(2) Provisione uma EC2 t3.micro (ou e2-micro / B1s) em duas regiões "
                    "diferentes, anote o tempo desde 'click' até 'SSH responde'.<br>"
                    "(3) De cada VM, use <code>mtr</code> / <code>traceroute</code> para a "
                    "outra e meça a latência cross-region.<br>"
                    "(4) Suba uma imagem Docker simples na mesma VM e cronometre o tempo de "
                    "subir uma instância nova vs subir um container, compare ordens de "
                    "magnitude.<br>"
                    "(5) Configure <strong>budget alert</strong> em US$ 5 e termine "
                    "(<code>terminate</code>) tudo no fim. <strong>Não esqueça.</strong> Se "
                    "esquecer, vai descobrir o mundo dos NAT Gateways de US$ 32/mês."
                ),
                "practical_en": (
                    "(1) Create a free-tier AWS account (or the GCP / Azure equivalent).<br>"
                    "(2) Provision a t3.micro EC2 instance (or e2-micro / B1s) in two different "
                    "regions, and note the time from 'click' to 'SSH responds'.<br>"
                    "(3) From each VM, use <code>mtr</code> / <code>traceroute</code> to reach the "
                    "other one and measure the cross-region latency.<br>"
                    "(4) Upload a simple Docker image to the same VM and time how long it takes to "
                    "bring up a new instance vs bringing up a container, and compare orders of "
                    "magnitude.<br>"
                    "(5) Set up a <strong>budget alert</strong> at US$5 and terminate "
                    "(<code>terminate</code>) everything at the end. <strong>Don't forget.</strong> If "
                    "you do, you'll discover the world of US$32/month NAT Gateways."
                ),
            },
            "materials": [
                m("AWS What is cloud computing?",
                  "https://aws.amazon.com/what-is-cloud-computing/", "article", "",
                  title_en="AWS What is cloud computing?", description_en=""),
                m("KVM Documentation",
                  "https://www.linux-kvm.org/page/Documents", "docs", "",
                  title_en="KVM Documentation", description_en=""),
                m("Microsoft: Cloud computing dictionary",
                  "https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/",
                  "article", "",
                  title_en="Microsoft: Cloud computing dictionary", description_en=""),
                m("Container vs VM (Docker)",
                  "https://www.docker.com/resources/what-container/", "article", "",
                  title_en="Container vs VM (Docker)", description_en=""),
                m("CNCF Glossary", "https://glossary.cncf.io/", "docs",
                  "Mantém termos atualizados de cloud-native.",
                  title_en="CNCF Glossary", description_en="Keeps cloud-native terminology up to date."),
                m("Linux Foundation: Open source cloud landscape",
                  "https://landscape.cncf.io/", "tool", "",
                  title_en="Linux Foundation: Open source cloud landscape", description_en=""),
            ],
            "questions": [
                q("O que é um hypervisor tipo 1?",
                  "Roda direto no hardware, sem SO host.",
                  ["É um tipo de container isolado por namespace do kernel.",
                   "Substitui o BIOS da placa-mãe por um firmware customizado.",
                   "Roda dentro de outro sistema operacional já instalado antes."],
                  "Tipo 1 = bare-metal (KVM, ESXi, Hyper-V). Tipo 2 = roda como app dentro de "
                  "outro SO (VirtualBox).",
                  statement_en="What is a type 1 hypervisor?",
                  correct_en="Runs directly on the hardware, with no host OS.",
                  wrong_en=["It's a type of container isolated by kernel namespaces.",
                            "It replaces the motherboard's BIOS with custom firmware.",
                            "It runs inside another operating system already installed."],
                  explanation_en="Type 1 = bare-metal (KVM, ESXi, Hyper-V). Type 2 runs as an app "
                  "inside another OS (VirtualBox)."),
                q("Cloud difere de virtualização porque:",
                  "Adiciona APIs, self-service e billing por uso.",
                  ["Não usa hardware físico algum durante a execução da carga.",
                   "Não oferece suporte ao sistema operacional Linux em seu catálogo.",
                   "Não tem rede alguma conectando os servidores do datacenter."],
                  "Virtualização é fundação técnica; cloud junta automação, multi-tenancy e billing.",
                  statement_en="Cloud differs from virtualization because it:",
                  correct_en="Adds APIs, self-service, and usage-based billing.",
                  wrong_en=["Uses no physical hardware while running any workload.",
                            "Doesn't support the Linux operating system in its catalog.",
                            "Has no network connecting the datacenter's servers whatsoever."],
                  explanation_en="Virtualization is the technical foundation; cloud adds automation, "
                  "multi-tenancy, and billing."),
                q("VM e container compartilham:",
                  "O hardware via virtualização (mesmo host físico).",
                  ["O mesmo hypervisor rodando abaixo de ambos ao mesmo tempo.",
                   "O mesmo kernel do sistema operacional hospedeiro compartilhado.",
                   "O mesmo endereço IP público atribuído à interface de rede."],
                  "Containers compartilham kernel; VMs têm kernel próprio. Ambos podem rodar no mesmo host.",
                  statement_en="A VM and a container share:",
                  correct_en="The hardware via virtualization (same physical host).",
                  wrong_en=["The same hypervisor running underneath both at the same time.",
                            "The same kernel of the shared host OS.",
                            "The same public IP address assigned to the network interface."],
                  explanation_en="Containers share the kernel; VMs have their own kernel. Both can "
                  "run on the same host."),
                q("Vantagem de cloud para startups:",
                  "Capex baixo e elasticidade.",
                  ["Hardware proprietário.",
                   "Sem necessidade de monitoramento.",
                   "Latência zero."],
                  "Pay-as-you-go evita compra de hardware para pico que pode nem existir.",
                  statement_en="Advantage of cloud for startups:",
                  correct_en="Low capex and elasticity.",
                  wrong_en=["Proprietary hardware.",
                            "No need for monitoring or alerting infrastructure whatsoever.",
                            "Zero latency."],
                  explanation_en="Pay-as-you-go avoids buying hardware for a peak that might never "
                  "even happen."),
                q("Tipo de cloud onde recursos são exclusivos da empresa:",
                  "Private cloud.",
                  ["Edge cloud, computação posicionada fisicamente perto do usuário final.",
                   "Hybrid cloud, combinação de nuvem pública e privada ao mesmo tempo.",
                   "Public cloud, infraestrutura compartilhada entre múltiplos clientes diferentes."],
                  "Pode ser on-premise (datacenter próprio) ou VPC dedicada num provedor público.",
                  statement_en="Type of cloud where resources are exclusive to the company:",
                  correct_en="Private cloud.",
                  wrong_en=["Edge cloud, computing positioned physically close to the end user.",
                            "Hybrid cloud, a combination of public and private cloud at once.",
                            "Public cloud, infrastructure shared among multiple different customers."],
                  explanation_en="Can be on-premise (your own datacenter) or a dedicated VPC in a "
                  "public provider."),
                q("Qual hypervisor é open source e parte do kernel Linux?",
                  "KVM",
                  ["VMware ESXi", "Hyper-V", "Xen Server proprietary"],
                  "KVM ('Kernel-based Virtual Machine') é módulo do kernel; libvirt e QEMU "
                  "completam o ecossistema.",
                  statement_en="Which hypervisor is open source and part of the Linux kernel?",
                  correct_en="KVM",
                  wrong_en=["VMware ESXi", "Hyper-V", "Xen Server proprietary"],
                  explanation_en="KVM ('Kernel-based Virtual Machine') is a kernel module; libvirt "
                  "and QEMU complete the ecosystem."),
                q("'Pay-as-you-go' refere-se a:",
                  "Cobrar pelo uso real, sem compromisso de longo prazo.",
                  ["Pagar o valor inteiro antecipado antes de sequer usar o serviço.",
                   "Usar o serviço de graça enquanto ele estiver ativo e funcionando.",
                   "Pagar só se o projeto for bem-sucedido no fim do ano."],
                  "Em muitos serviços (S3, Lambda, Run) você paga por requisição/byte. Em VMs, por hora/segundo.",
                  statement_en="'Pay-as-you-go' refers to:",
                  correct_en="Charging for actual usage, with no long-term commitment.",
                  wrong_en=["Paying the full amount upfront before even using the service.",
                            "Using the service for free while it stays active and running.",
                            "Paying just if the project succeeds by the end of the year."],
                  explanation_en="In many services (S3, Lambda, Run) you pay per request/byte. On "
                  "VMs, per hour/second."),
                q("Multi-tenancy implica:",
                  "Múltiplos clientes compartilhando infra com isolamento.",
                  ["Banco de dados único, sem separação lógica entre registro de cliente diferente.",
                   "Ausência completa de segregação entre carga de trabalho diferente.",
                   "Só um cliente autorizado a usar cada servidor físico por vez."],
                  "Isolamento via namespaces, IAM, redes virtuais. Provedor garante que tenant A não vê tenant B.",
                  statement_en="Multi-tenancy implies:",
                  correct_en="Multiple customers sharing infrastructure with isolation.",
                  wrong_en=["A single database, with no logical separation between different customer records.",
                            "Complete absence of segregation between different workloads.",
                            "A single customer authorized to use each physical server at a time."],
                  explanation_en="Isolation via namespaces, IAM, virtual networks. The provider "
                  "guarantees tenant A never sees tenant B."),
                q("Region em cloud é:",
                  "Conjunto geográfico de datacenters (várias AZs).",
                  ["Um endereço IP público atribuído a uma única instância específica.",
                   "Uma role de IAM concedendo permissão de acesso a um recurso.",
                   "Uma máquina física específica dentro de um datacenter qualquer."],
                  "Ex.: us-east-1 tem múltiplas AZs (us-east-1a, 1b, 1c). Latência baixa entre AZs, alta entre regiões.",
                  statement_en="A region in cloud is:",
                  correct_en="A geographic set of datacenters (multiple AZs).",
                  wrong_en=["A public IP address assigned to one specific instance.",
                            "An IAM role granting permission to access a resource.",
                            "One specific physical machine inside some datacenter."],
                  explanation_en="E.g.: us-east-1 has multiple AZs (us-east-1a, 1b, 1c). Latency is "
                  "low between AZs, higher between regions."),
                q("Disponibilidade aumenta com:",
                  "Distribuir cargas entre múltiplas Availability Zones.",
                  ["Reduzir o número de réplica ativa para economizar custo de operação.",
                   "Fazer backup periódico só do banco de dados principal da aplicação.",
                   "Usar um único disco SSD de alta performance sem redundância alguma."],
                  "AZ é falha unitária, se uma cair, as outras sobrevivem se você arquitetou multi-AZ.",
                  statement_en="Availability increases with:",
                  correct_en="Distributing workloads across multiple Availability Zones.",
                  wrong_en=["Reducing the number of active replicas to save on operating cost.",
                            "Just doing periodic backups of the application's main database.",
                            "Using a single high-performance SSD disk with no redundancy whatsoever."],
                  explanation_en="An AZ is the unit of failure — if one goes down, the others survive "
                  "if you architected for multi-AZ."),
            ],
        },
        # =====================================================================
        # 2.2 Shared Responsibility Model
        # =====================================================================
        {
            "title": "Shared Responsibility Model",
            "title_en": "Shared Responsibility Model",
            "summary": "O que é dever da AWS/Azure/GCP e o que é seu.",
            "summary_en": "What's on AWS/Azure/GCP to handle, and what's on you.",
            "lesson": {
                "intro": (
                    "'Mas eu pensei que a AWS cuidasse disso' é a frase mais cara que se diz "
                    "em incidente de cloud. Cada provedor publica explicitamente onde a "
                    "responsabilidade dele termina e a sua começa, e violação de S3 público, "
                    "credenciais hard-coded, RDS sem backup raramente são 'culpa do "
                    "provedor'. São culpa de quem não leu o contrato.<br><br>"
                    "Esta aula desconstrói o Shared Responsibility Model com exemplos "
                    "concretos por serviço, mostra os mitos mais perigosos e dá um "
                    "framework para auditar 'quem é responsável por X' em cada componente "
                    "do seu stack."
                ),
                "intro_en": (
                    "'But I thought AWS took care of that' is the most expensive sentence "
                    "said during a cloud incident. Every provider explicitly publishes where "
                    "its responsibility ends and yours begins, and a public S3 bucket, "
                    "hard-coded credentials, an RDS instance with no backup are rarely "
                    "'the provider's fault'. They're the fault of whoever didn't read the "
                    "contract.<br><br>"
                    "This lesson breaks down the Shared Responsibility Model with concrete "
                    "examples per service, shows the most dangerous myths, and gives a "
                    "framework for auditing 'who is responsible for X' in every component "
                    "of your stack."
                ),
                "body": (
                """<h3>1. A linha móvel: quanto mais alto o serviço, mais o provedor cobre</h3>
<p>A divisão de responsabilidade muda de acordo com o nível de
abstração escolhido:</p>
<div class="mermaid">
flowchart TD
    subgraph Provedor ["Responsabilidade do provedor"]
        P1["Datacenter físico"]
        P2["Hardware e rede"]
        P3["Hypervisor"]
    end
    subgraph Cliente ["Responsabilidade do cliente"]
        C1["Configuração de IAM"]
        C2["Dado armazenado"]
        C3["Patch do sistema operacional"]
        C4["Configuração de security group"]
    end
</div>

<table>
<tr><th>Camada</th><th>On-prem</th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>
<tr><td>Datacenter, energia</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>
<tr><td>Rede física, hardware</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>
<tr><td>Hypervisor</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>
<tr><td>SO, patches</td><td>você</td><td>VOCÊ</td><td>provedor</td><td>provedor</td></tr>
<tr><td>Runtime (libs, JVM, Python)</td><td>você</td><td>VOCÊ</td><td>provedor</td><td>provedor</td></tr>
<tr><td>Aplicação</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>provedor</td></tr>
<tr><td>Configuração de segurança</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>
<tr><td>Identidades, MFA</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>
<tr><td>Dados</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>
</table>
<p>O detalhe mais importante dessa tabela não é onde a linha se move —
é onde ela NUNCA se move: identidade, configuração de segurança e dado
permanecem do lado do cliente em absolutamente todos os quatro modelos,
até no SaaS mais gerenciado que existe.</p>

<h3>2. Os três grandes, visão oficial</h3>
<p>Cada provedor formula o mesmo princípio com ênfase ligeiramente
diferente. A AWS separa Security <em>OF</em> the Cloud (o provedor
protege a infraestrutura em si) de Security <em>IN</em> the Cloud (você
protege o que roda dentro dela). O Azure documenta uma matriz de
"Shared Responsibility" detalhada serviço por serviço. E o GCP vai um
passo além com "Shared Responsibility &amp; Shared Fate" — um
compromisso ativo de ajudar o cliente a acertar, com default já
configurado de forma mais segura, em vez de simplesmente empurrar a
responsabilidade inteira para o outro lado e esperar que a
documentação seja lida.</p>

<h3>3. Caso a caso: o que muda por serviço</h3>
<p>Mesmo dentro do mesmo provedor, a divisão exata varia bastante
conforme o serviço específico:</p>
<table>
<tr><th>Serviço</th><th>Você cuida de</th><th>Provedor cuida de</th></tr>
<tr><td>EC2 (IaaS)</td><td>SO, patches, app, dados, IAM, SG, dados</td>
<td>hypervisor, hardware, rede física</td></tr>
<tr><td>RDS (PaaS-DB)</td><td>schema, queries, backup config, IAM,
dados, encryption keys</td>
<td>SO, patches do MySQL/PG, replicação, HA, hardware</td></tr>
<tr><td>Lambda (FaaS)</td><td>código, deps, IAM, segredos, dados</td>
<td>SO, runtime, escala, hardware, isolamento</td></tr>
<tr><td>S3 (object storage)</td><td>policy, encryption keys, public access,
lifecycle, conteúdo dos objetos</td>
<td>durabilidade, hardware, encryption infra</td></tr>
<tr><td>EKS (managed K8s)</td><td>worker nodes, workloads, RBAC, network
policy, dados</td>
<td>control plane, etcd, upgrades do plane</td></tr>
<tr><td>M365 (SaaS)</td><td>identidades, compartilhamentos, retenção,
DLP, MFA</td>
<td>app, infra, disponibilidade</td></tr>
</table>

<h3>4. O que SEMPRE é seu, em qualquer serviço</h3>
<p>Seis áreas permanecem responsabilidade do cliente independentemente
de quão gerenciado o serviço seja. Identidade e acesso — usuário,
role, MFA, policy — continuam seus mesmo no Gmail, onde configurar sua
própria MFA continua sendo problema seu, não do Google. Classificação e
proteção de dado exige decidir explicitamente o que é público, interno,
PII ou financeiro — a ferramenta de DLP existe, mas configurá-la de
acordo com essa classificação é trabalho seu. Configuração de segurança
— bucket público, security group aberto para <code>0.0.0.0/0</code>,
RDS sem encryption — é sempre sua, porque só você conhece o contexto de
negócio de cada recurso. Backup configurável — retenção, frequência,
replicação cross-region — precisa de ajuste ativo, porque o default do
provedor tende a ser minimalista por design. Log e monitoramento
(CloudTrail, CloudWatch, GuardDuty) existem prontos, mas alguém precisa
habilitá-los e mandar o output para um lugar seguro e monitorado. E
compliance dos SEUS controles específicos não se resolve pela
certificação do provedor — o SOC 2 da AWS não certifica automaticamente
a sua própria configuração dentro dela.</p>

<h3>5. Misconfiguration é a causa #1, dados</h3>
<p>O Verizon DBIR de 2024 aponta que 31% das violações em cloud
envolveram misconfiguration — não exploit sofisticado, mas
configuração simplesmente errada. O Gartner projeta que 99% dos
incidentes em cloud até 2025 serão atribuíveis ao cliente, não ao
provedor. Os padrões recorrentes formam uma lista quase repetitiva de
incidente para incidente: bucket S3 com leitura pública (Verizon,
Accenture, Capital One — todos passaram por isso); security group com
SSH ou RDP aberto para <code>0.0.0.0/0</code>; conta root sem MFA;
access key hard-coded acabando em repositório público do GitHub (cerca
de 50 mil vazam por ano); RDS sem encryption at rest, sem backup
configurado, sem snapshot cross-region; IAM com
<code>AdministratorAccess</code> concedido a uma aplicação; IP público
em container ou função deixado "só para teste" e nunca removido depois;
e CloudTrail simplesmente desligado na conta inteira.</p>

<h3>6. Guard-rails: prevenir em vez de detectar</h3>
<p>Em vez de torcer para cada time configurar certo manualmente,
guard-rail IMPEDE a configuração insegura antes dela existir. Na AWS,
isso é SCP (Service Control Policy) em Organizations, AWS Config Rules
combinado com Conformance Packs, Trusted Advisor e Security Hub. No
Azure, é Azure Policy (nos modos deny, audit ou append) combinado com
Defender for Cloud. No GCP, são Organization Policies combinadas com
Security Command Center. E em ambiente multi-cloud, ferramentas como
Cloud Custodian (open source), Wiz, Prisma Cloud ou Lacework cobrem o
mesmo papel de forma unificada entre provedores diferentes. Um exemplo
concreto de SCP que impede desligar o Block Public Access de qualquer
bucket:</p>
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": ["s3:PutBucketPublicAccessBlock"],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {"s3:PublicAccessBlock": "true"}
    }
  }]
}</code></pre>

<h3>7. Como ler a documentação do provedor</h3>
<p>Cada serviço publica sua própria matriz de responsabilidade
específica, e em ambiente regulado essa leitura deixa de ser opcional:
os Service Specific Terms da AWS (ou Service Description no Azure)
detalham o serviço em si; o Data Processing Addendum (DPA) é exigência
direta de LGPD e GDPR; o Trust &amp; Compliance Center de cada provedor
lista certificação como ISO 27001, SOC 2, PCI e HIPAA; e os Customer
Compliance Guides deixam explícito o que é seu e o que é do provedor
para cada serviço específico. Não assinar contrato sem ler essa
documentação evita a situação mais desconfortável possível: num
incidente real, a primeira pergunta de um auditor costuma ser
literalmente "mostre o contrato e o controle correspondente".</p>

<h3>8. Modelo PaaS = mais cuidado, não menos</h3>
<p>Um mito perigoso e recorrente: "Lambda é serverless, não tem
servidor para eu mesmo aplicar patch, então não preciso me preocupar
com mais nada". Em FaaS, cinco responsabilidades continuam
inteiramente do lado do cliente: vulnerabilidade nas próprias
dependências (o Log4Shell afetava função Lambda em Java exatamente da
mesma forma que qualquer outro ambiente Java); permissão IAM da função
(uma role de Lambda com <code>S3:*</code> concedido é receita pronta
para um SSRF virar exfiltração total, como no caso Capital One da seção
9); validação de input; gestão de segredo e chave; e log e
monitoramento, que sim, continuam necessários mesmo sem servidor
visível para o cliente administrar diretamente. O provedor cobre menos
CAMADAS em FaaS, mas o que sobra é justamente onde vivem as
vulnerabilidades mais comuns do OWASP Top 10.</p>

<h3>9. Caso real: Capital One 2019, anatomia de uma violação cloud</h3>
<p>A cadeia completa do incidente segue quatro passos, e nenhum deles
é falha da AWS: um WAF mal configurado — problema do CLIENTE — permitia
SSRF; o SSRF apontado para
<code>http://169.254.169.254/latest/meta-data/iam/...</code> (o
serviço de metadados da própria AWS) devolveu credencial temporária da
role atrelada à instância EC2; essa role tinha
<code>s3:ListAllMyBuckets</code> e <code>s3:GetObject</code> liberado
para TODOS os buckets da empresa — uma violação direta do princípio do
menor privilégio, de novo problema do cliente, não do provedor; e o
atacante, com essa credencial em mãos, listou e baixou 100 milhões de
registros. Em nenhum momento a AWS falhou tecnicamente — a
infraestrutura funcionou exatamente como projetada. Os controles que
falharam foram todos do lado do cliente: WAF, IAM, rede e monitoramento
(que sequer detectou a exfiltração enquanto acontecia). A resposta da
AWS depois desse incidente incluiu lançar o IMDSv2 (baseado em token,
exigindo <code>PUT</code> explícito, o que mitiga esse tipo específico
de SSRF), ativar Block Public Access como default em bucket novo, e
lançar o IAM Access Analyzer — mas nenhuma dessas mudanças TIRA a
responsabilidade do cliente, elas só tornam mais fácil configurar
certo desde o início.</p>

<h3>10. Checklist mensal de Shared Responsibility</h3>
<ol>
<li>Conta root tem MFA hardware? (Root nunca deveria ser usado no
dia a dia.)</li>
<li>CloudTrail está ativo em TODAS as regiões, com log num bucket
imutável e separado?</li>
<li>Block Public Access está ativado para a conta inteira, não só
bucket por bucket?</li>
<li>Existe SCP ou Policy bloqueando criação de recurso sem
encryption?</li>
<li>Existe SCP ou Policy bloqueando região fora das aprovadas
explicitamente?</li>
<li>Security Hub, Defender ou Security Command Center está habilitado
E sendo revisado de fato, não só ligado?</li>
<li>GuardDuty, Defender for Cloud ou SCC tem alerta crítico
efetivamente encaminhado para alguém agir?</li>
<li>Backup está configurado E testado — não só configurado — em todo
RDS?</li>
<li>Access key do IAM com mais de 90 dias já foi rotacionada?</li>
<li>Todo recurso está tagueado com <code>Owner</code> e
<code>Environment</code>?</li>
</ol>"""
                ),
                "body_en": (
                """<h3>1. The moving line: the higher the service, the more the provider covers</h3>
<p>The division of responsibility changes depending on the level of
abstraction chosen:</p>
<div class="mermaid">
flowchart TD
    subgraph Provedor ["Responsabilidade do provedor"]
        P1["Datacenter físico"]
        P2["Hardware e rede"]
        P3["Hypervisor"]
    end
    subgraph Cliente ["Responsabilidade do cliente"]
        C1["Configuração de IAM"]
        C2["Dado armazenado"]
        C3["Patch do sistema operacional"]
        C4["Configuração de security group"]
    end
</div>

<table>
<tr><th>Layer</th><th>On-prem</th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>
<tr><td>Datacenter, power</td><td>you</td><td>provider</td><td>provider</td><td>provider</td></tr>
<tr><td>Physical network, hardware</td><td>you</td><td>provider</td><td>provider</td><td>provider</td></tr>
<tr><td>Hypervisor</td><td>you</td><td>provider</td><td>provider</td><td>provider</td></tr>
<tr><td>OS, patches</td><td>you</td><td>YOU</td><td>provider</td><td>provider</td></tr>
<tr><td>Runtime (libs, JVM, Python)</td><td>you</td><td>YOU</td><td>provider</td><td>provider</td></tr>
<tr><td>Application</td><td>you</td><td>YOU</td><td>YOU</td><td>provider</td></tr>
<tr><td>Security configuration</td><td>you</td><td>YOU</td><td>YOU</td><td>YOU</td></tr>
<tr><td>Identities, MFA</td><td>you</td><td>YOU</td><td>YOU</td><td>YOU</td></tr>
<tr><td>Data</td><td>you</td><td>YOU</td><td>YOU</td><td>YOU</td></tr>
</table>
<p>The most important detail in this table isn't where the line moves —
it's where it NEVER moves: identity, security configuration, and data
stay on the customer's side across all four models,
even in the most fully managed SaaS that exists.</p>

<h3>2. The three big ones, official view</h3>
<p>Each provider states the same principle with slightly
different emphasis. AWS separates Security <em>OF</em> the Cloud (the provider
protects the infrastructure itself) from Security <em>IN</em> the Cloud (you
protect what runs inside it). Azure documents a detailed
"Shared Responsibility" matrix, service by service. And GCP goes one
step further with "Shared Responsibility &amp; Shared Fate" — an
active commitment to help the customer get it right, with more secure
defaults already configured, instead of simply pushing the
entire responsibility to the other side and hoping the
documentation gets read.</p>

<h3>3. Case by case: what changes per service</h3>
<p>Even within the same provider, the exact split varies a lot
depending on the specific service:</p>
<table>
<tr><th>Service</th><th>You handle</th><th>Provider handles</th></tr>
<tr><td>EC2 (IaaS)</td><td>OS, patches, app, data, IAM, SG, data</td>
<td>hypervisor, hardware, physical network</td></tr>
<tr><td>RDS (PaaS-DB)</td><td>schema, queries, backup config, IAM,
data, encryption keys</td>
<td>OS, MySQL/PG patches, replication, HA, hardware</td></tr>
<tr><td>Lambda (FaaS)</td><td>code, deps, IAM, secrets, data</td>
<td>OS, runtime, scaling, hardware, isolation</td></tr>
<tr><td>S3 (object storage)</td><td>policy, encryption keys, public access,
lifecycle, object content</td>
<td>durability, hardware, encryption infra</td></tr>
<tr><td>EKS (managed K8s)</td><td>worker nodes, workloads, RBAC, network
policy, data</td>
<td>control plane, etcd, control plane upgrades</td></tr>
<tr><td>M365 (SaaS)</td><td>identities, sharing settings, retention,
DLP, MFA</td>
<td>app, infra, availability</td></tr>
</table>

<h3>4. What is ALWAYS yours, in any service</h3>
<p>Six areas remain the customer's responsibility no matter
how managed the service is. Identity and access — user,
role, MFA, policy — remain yours even in Gmail, where setting up your
own MFA is still your problem, not Google's. Data classification and
protection requires explicitly deciding what's public, internal,
PII, or financial — the DLP tool exists, but configuring it
according to that classification is your job. Security configuration
— a public bucket, a security group open to <code>0.0.0.0/0</code>,
an unencrypted RDS instance — is always yours, because only you know the
business context of each resource. Configurable backup — retention,
frequency, cross-region replication — needs active tuning, because the
provider's default tends to be minimalist by design. Logging and monitoring
(CloudTrail, CloudWatch, GuardDuty) exist out of the box, but someone needs
to turn them on and route the output somewhere secure and monitored. And
compliance for YOUR specific controls isn't solved by the provider's
certification — AWS's SOC 2 doesn't automatically certify
your own configuration inside it.</p>

<h3>5. Misconfiguration is cause #1, by the data</h3>
<p>The 2024 Verizon DBIR points out that 31% of cloud breaches
involved misconfiguration — not a sophisticated exploit, but
simply wrong configuration. Gartner projects that 99% of
cloud incidents through 2025 will be attributable to the customer, not the
provider. The recurring patterns form an almost repetitive list from
incident to incident: a publicly readable S3 bucket (Verizon,
Accenture, Capital One — all went through this); a security group with
SSH or RDP open to <code>0.0.0.0/0</code>; a root account with no MFA;
a hard-coded access key ending up in a public GitHub repository (about
50 thousand leak per year); RDS with no encryption at rest, no backup
configured, no cross-region snapshot; IAM with
<code>AdministratorAccess</code> granted to an application; a public IP
on a container or function left "just for testing" and never removed later;
and CloudTrail simply turned off across the entire account.</p>

<h3>6. Guard-rails: prevent instead of detect</h3>
<p>Instead of hoping every team configures things correctly by hand,
a guard-rail PREVENTS the insecure configuration from ever existing. On
AWS, that's SCP (Service Control Policy) in Organizations, AWS Config Rules
combined with Conformance Packs, Trusted Advisor, and Security Hub. On
Azure, it's Azure Policy (in deny, audit, or append modes) combined with
Defender for Cloud. On GCP, it's Organization Policies combined with
Security Command Center. And in a multi-cloud environment, tools like
Cloud Custodian (open source), Wiz, Prisma Cloud, or Lacework cover the
same role in a unified way across different providers. A concrete
example of an SCP that blocks turning off Block Public Access on any
bucket:</p>
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": ["s3:PutBucketPublicAccessBlock"],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {"s3:PublicAccessBlock": "true"}
    }
  }]
}</code></pre>

<h3>7. How to read the provider's documentation</h3>
<p>Every service publishes its own specific responsibility
matrix, and in a regulated environment reading it stops being optional:
AWS's Service Specific Terms (or Service Description on Azure)
detail the service itself; the Data Processing Addendum (DPA) is a direct
requirement of LGPD and GDPR; each provider's Trust &amp; Compliance Center
lists certifications like ISO 27001, SOC 2, PCI, and HIPAA; and
Customer Compliance Guides spell out explicitly what's yours and what's the
provider's for each specific service. Not signing a contract without reading
this documentation avoids the most uncomfortable situation possible:
in a real incident, an auditor's first question tends to
literally be "show me the contract and the corresponding control".</p>

<h3>8. The PaaS model means more care, not less</h3>
<p>A dangerous and recurring myth: "Lambda is serverless, there's no
server for me to patch myself, so I don't need to worry
about anything else". In FaaS, five responsibilities remain
entirely on the customer's side: vulnerabilities in your own
dependencies (Log4Shell affected a Java Lambda function exactly the
same way as any other Java environment); the function's IAM permissions
(a Lambda role granted <code>S3:*</code> is a ready-made recipe
for an SSRF to turn into total exfiltration, as in the Capital One case in
section 9); input validation; secret and key management; and
logging and monitoring, which, yes, remain necessary even without a
server visible for the customer to directly administer. The provider covers
fewer LAYERS in FaaS, but what's left is precisely where the most
common OWASP Top 10 vulnerabilities live.</p>

<h3>9. Real case: Capital One 2019, anatomy of a cloud breach</h3>
<p>The full chain of the incident follows four steps, and none of them
is AWS's fault: a misconfigured WAF — a CUSTOMER problem — allowed
SSRF; the SSRF pointed at
<code>http://169.254.169.254/latest/meta-data/iam/...</code> (AWS's own
metadata service) returned a temporary credential for the
role attached to the EC2 instance; that role had
<code>s3:ListAllMyBuckets</code> and <code>s3:GetObject</code> granted
for ALL of the company's buckets — a direct violation of the least-privilege
principle, again a customer problem, not the provider's; and the
attacker, with that credential in hand, listed and downloaded 100 million
records. At no point did AWS fail technically — the
infrastructure worked exactly as designed. The controls that
failed were all on the customer's side: WAF, IAM, network, and monitoring
(which didn't even detect the exfiltration while it was happening). AWS's
response after this incident included launching IMDSv2 (token-based,
requiring an explicit <code>PUT</code>, which mitigates this specific type
of SSRF), enabling Block Public Access as the default on new buckets, and
launching IAM Access Analyzer — but none of these changes REMOVE the
customer's responsibility, they just make it easier to configure
correctly from the start.</p>

<h3>10. Monthly Shared Responsibility checklist</h3>
<ol>
<li>Does the root account have hardware MFA? (Root should never be used
day to day.)</li>
<li>Is CloudTrail active in ALL regions, with logs in an immutable,
separate bucket?</li>
<li>Is Block Public Access enabled for the entire account, not just
bucket by bucket?</li>
<li>Is there an SCP or Policy blocking resource creation without
encryption?</li>
<li>Is there an SCP or Policy blocking any region outside the explicitly
approved ones?</li>
<li>Is Security Hub, Defender, or Security Command Center enabled
AND actually being reviewed, not just turned on?</li>
<li>Does GuardDuty, Defender for Cloud, or SCC have a critical alert
actually routed to someone who will act on it?</li>
<li>Is backup configured AND tested — not just configured — on every
RDS instance?</li>
<li>Has any IAM access key older than 90 days been rotated?</li>
<li>Is every resource tagged with <code>Owner</code> and
<code>Environment</code>?</li>
</ol>"""
                ),
                "practical": (
                    "Crie um spreadsheet 3x10:<br>"
                    "Linhas: 10 itens de operação (patch SO, patch DB engine, snapshot RDS, "
                    "encryption at rest, MFA root, logs CloudTrail, gestão de IAM, public "
                    "access, backup S3, configuração de SG).<br>"
                    "Colunas: Você / Provedor / Compartilhado.<br>"
                    "Para cada combinação, escreva 1 frase justificando. Cruze com a página "
                    "oficial do seu provedor, para cada item que você marcou 'provedor', "
                    "ache a citação textual. Provavelmente vai descobrir 2-3 itens que você "
                    "achava deles e na verdade são seus."
                ),
                "practical_en": (
                    "Create a 3x10 spreadsheet:<br>"
                    "Rows: 10 operational items (OS patching, DB engine patching, RDS snapshot, "
                    "encryption at rest, root MFA, CloudTrail logs, IAM management, public "
                    "access, S3 backup, SG configuration).<br>"
                    "Columns: You / Provider / Shared.<br>"
                    "For each combination, write 1 sentence justifying it. Cross-check against "
                    "your provider's official page — for every item you marked 'provider', "
                    "find the exact quote. You'll probably discover 2-3 items you thought were "
                    "theirs that are actually yours."
                ),
            },
            "materials": [
                m("AWS Shared Responsibility Model",
                  "https://aws.amazon.com/compliance/shared-responsibility-model/", "docs", "",
                  title_en="AWS Shared Responsibility Model", description_en=""),
                m("Azure Shared Responsibility",
                  "https://learn.microsoft.com/azure/security/fundamentals/shared-responsibility",
                  "docs", "",
                  title_en="Azure Shared Responsibility", description_en=""),
                m("Google: Shared responsibility on Google Cloud",
                  "https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate",
                  "docs", "",
                  title_en="Google: Shared responsibility on Google Cloud", description_en=""),
                m("CIS Benchmarks", "https://www.cisecurity.org/cis-benchmarks/", "docs", "",
                  title_en="CIS Benchmarks", description_en=""),
                m("CSA Cloud Controls Matrix",
                  "https://cloudsecurityalliance.org/research/cloud-controls-matrix/", "docs", "",
                  title_en="CSA Cloud Controls Matrix", description_en=""),
                m("Verizon DBIR (relatório anual)",
                  "https://www.verizon.com/business/resources/reports/dbir/", "article", "",
                  title_en="Verizon DBIR (annual report)", description_en=""),
            ],
            "questions": [
                q("Em IaaS, quem é responsável pelo SO da VM?",
                  "O cliente.",
                  ["O provedor.", "Compartilhado 50/50.", "Ninguém."],
                  "Cliente responde por patch, configuração, agentes. Provedor só fornece o substrato físico.",
                  statement_en="In IaaS, who is responsible for the VM's OS?",
                  correct_en="The customer.",
                  wrong_en=["The provider.", "Shared 50/50.", "No one."],
                  explanation_en="The customer handles patching, configuration, agents. The "
                  "provider only supplies the physical substrate."),
                q("O provedor de cloud é responsável por:",
                  "Segurança DA cloud (datacenter, hypervisor).",
                  ["Aplicar patch de segurança na aplicação do cliente rodando ali.",
                   "Configurar a política de IAM específica da conta do cliente.",
                   "Fazer backup do banco de dados que pertence ao cliente final."],
                  "DA cloud (segurança da infraestrutura) é do provedor; NA cloud (o que você roda nela) é seu.",
                  statement_en="The cloud provider is responsible for:",
                  correct_en="Security OF the cloud (datacenter, hypervisor).",
                  wrong_en=["Applying security patches to the customer's application running there.",
                            "Configuring the customer account's specific IAM policy.",
                            "Backing up the database that belongs to the end customer."],
                  explanation_en="Security OF the cloud (infrastructure security) is the "
                  "provider's; security IN the cloud (what you run in it) is yours."),
                q("Em SaaS típico, o que ainda é dever do cliente?",
                  "Identidades, dados e configuração.",
                  ["O hardware físico do datacenter onde o serviço realmente roda.",
                   "O sistema operacional completo da máquina virtual subjacente.",
                   "O hypervisor que isola cada cliente dentro do mesmo servidor físico."],
                  "Mesmo no SaaS, gerência de usuários, MFA e classificação de dados não saem do cliente.",
                  statement_en="In typical SaaS, what still falls on the customer?",
                  correct_en="Identities, data, and configuration.",
                  wrong_en=["The physical hardware of the datacenter where the service actually runs.",
                            "The complete operating system of the underlying virtual machine.",
                            "The hypervisor that isolates each customer within the same physical server."],
                  explanation_en="Even in SaaS, user management, MFA, and data classification "
                  "never leave the customer's hands."),
                q("Quem responde por uma S3 mal configurado e público?",
                  "O cliente, é configuração dele.",
                  ["É um bug conhecido da própria AWS, sem relação com configuração.",
                   "O provedor assume, porque o bucket nasce protegido por padrão.",
                   "Responsabilidade dividida meio a meio entre cliente e provedor."],
                  "AWS oferece 'Block Public Access' habilitado por padrão; cliente desligou? Cliente respondeu.",
                  statement_en="Who is on the hook for a misconfigured, public S3 bucket?",
                  correct_en="The customer — it's their configuration.",
                  wrong_en=["It's a known AWS bug, unrelated to any configuration.",
                            "The provider takes it on, since buckets are born protected by default.",
                            "Responsibility split evenly between customer and provider."],
                  explanation_en="AWS ships 'Block Public Access' enabled by default; did the "
                  "customer turn it off? Then the customer answers for it."),
                q("Backup de dados em RDS é dever:",
                  "Do cliente, a AWS oferece a infraestrutura, mas o cliente configura snapshots e retenção.",
                  ["Do provedor, que garante backup automático completo em cada instância RDS criada por padrão de fábrica.",
                   "Da equipe de auditoria externa contratada especificamente para essa tarefa periódica de revisão.",
                   "RDS não oferece forma de backup automatizado ou manual disponível em qualquer plano contratado."],
                  "Snapshots automáticos têm retenção padrão curta; ajuste para sua janela de RTO/RPO.",
                  statement_en="Backing up RDS data is the duty of:",
                  correct_en="The customer — AWS provides the infrastructure, but the customer "
                  "configures snapshots and retention.",
                  wrong_en=["The provider, which guarantees full automatic backup on every RDS "
                            "instance created by factory default.",
                            "The external audit team specifically hired for that periodic review task.",
                            "RDS offers no automated or manual backup option available on any "
                            "contracted plan."],
                  explanation_en="Automatic snapshots have a short default retention; adjust it "
                  "for your RTO/RPO window."),
                q("Qual fator NÃO faz parte do shared responsibility?",
                  "Cor do logo da empresa.",
                  ["Identidade do usuário e política de acesso configurada por ele.",
                   "Dado armazenado e processado dentro de qualquer um dos serviços.",
                   "Rede virtual (VPC) e as regras de roteamento definidas pelo cliente."],
                  "Pegadinha, todos os outros são partes legítimas do modelo.",
                  statement_en="Which factor is NOT part of shared responsibility?",
                  correct_en="The color of the company's logo.",
                  wrong_en=["User identity and the access policy they configure.",
                            "Data stored and processed within any of the services.",
                            "Virtual network (VPC) and the routing rules defined by the customer."],
                  explanation_en="Trick question — all the others are legitimate parts of the "
                  "model."),
                q("Em IaaS, patch do kernel é:",
                  "Responsabilidade do cliente.",
                  ["Responsabilidade do provedor.",
                   "Não precisa ser feito.",
                   "Automatizado pela cloud."],
                  "Use Systems Manager/Update Management para automatizar, mas a responsabilidade é sua.",
                  statement_en="In IaaS, kernel patching is:",
                  correct_en="The customer's responsibility.",
                  wrong_en=["It is the provider's sole responsibility to handle this automatically.",
                            "It doesn't need to be done.",
                            "Automated by the cloud."],
                  explanation_en="Use Systems Manager/Update Management to automate it, but the "
                  "responsibility is yours."),
                q("Compliance é responsabilidade:",
                  "Compartilhada, cada parte certifica o que controla.",
                  ["Só do auditor externo contratado uma vez por ano pela empresa.",
                   "Só do provedor de nuvem, que certifica o datacenter inteiro sozinho.",
                   "Só do cliente, que precisa provar conformidade sem qualquer ajuda do provedor contratado."],
                  "Provedor mostra que o datacenter está conforme; cliente mostra que sua app/processo está conforme.",
                  statement_en="Compliance is the responsibility of:",
                  correct_en="Shared — each party certifies what it controls.",
                  wrong_en=["The external auditor hired once a year by the company, exclusively.",
                            "The cloud provider alone, which certifies the entire datacenter by itself.",
                            "The customer alone, who must prove compliance without any help from "
                            "the contracted provider."],
                  explanation_en="The provider shows the datacenter is compliant; the customer "
                  "shows their app/process is compliant."),
                q("Por que ler documentos do provedor?",
                  "Para saber o limite exato e não pressupor cobertura.",
                  ["Por exigência legal, sem motivo prático adicional relevante para o negócio.",
                   "Para virar parceiro comercial oficial certificado pelo provedor.",
                   "Para reduzir o custo mensal pago pela licença do serviço contratado."],
                  "Surpresas em incidente são caras; ler antes evita 'nossa, achei que vocês cuidassem disso'.",
                  statement_en="Why read the provider's documents?",
                  correct_en="To know the exact boundary and not assume coverage.",
                  wrong_en=["Purely a legal requirement, with no additional practical relevance "
                            "to the business.",
                            "To become an official certified commercial partner of the provider.",
                            "To reduce the monthly cost paid for the contracted service license."],
                  explanation_en="Surprises during an incident are expensive; reading beforehand "
                  "avoids 'oh, I thought you handled that'."),
                q("Configuração errada em segurança em cloud é a causa:",
                  "Mais comum de incidentes em cloud pública.",
                  ["Mais rara do que ataque direto à infraestrutura do provedor.",
                   "Atribuída exclusivamente ao provedor, independente da configuração do cliente.",
                   "Um problema restrito só à área de billing e cobrança do contrato."],
                  "Confirmado por DBIR, CSA, Gartner, AWS Well-Architected, misconfiguration domina o ranking.",
                  statement_en="Security misconfiguration in cloud is the:",
                  correct_en="Most common cause of incidents in public cloud.",
                  wrong_en=["Rarer cause than a direct attack on the provider's own infrastructure.",
                            "Cause attributed exclusively to the provider, regardless of the "
                            "customer's configuration.",
                            "Cause limited to the billing and invoicing side of the contract, "
                            "unrelated to security posture."],
                  explanation_en="Confirmed by DBIR, CSA, Gartner, AWS Well-Architected — "
                  "misconfiguration dominates the ranking."),
            ],
        },
        # =====================================================================
        # 2.3 IAM
        # =====================================================================
        {
            "title": "IAM (Identity and Access Management)",
            "title_en": "IAM (Identity and Access Management)",
            "summary": "Criação de usuários, grupos e roles com permissões restritas.",
            "summary_en": "Creating users, groups, and roles with restricted permissions.",
            "lesson": {
                "intro": (
                    "Em cloud moderna, IAM é mais importante que firewall. O perímetro tradicional "
                    "(rede) virou irrelevante quando você tem 200 contas, 50 países e milhares "
                    "de SaaSes integrados via API. O novo perímetro é a <em>identidade</em>.<br><br>"
                    "Quase todo comprometimento sério em cloud passa por uma identidade "
                    "poderosa que não deveria ser. Capital One (2019), SolarWinds (2020), "
                    "Uber (2022), Okta (2022), em cada um, uma identidade com privilégio "
                    "excessivo foi a peça que destrancou o resto. Saber IAM = saber sobreviver "
                    "ao S3-leak da semana."
                ),
                "intro_en": (
                    "In modern cloud, IAM matters more than the firewall. The traditional "
                    "(network) perimeter became irrelevant once you have 200 accounts, 50 "
                    "countries, and thousands of SaaS apps integrated via API. The new "
                    "perimeter is <em>identity</em>.<br><br>"
                    "Almost every serious cloud breach traces back to an identity with more "
                    "power than it should have had. Capital One (2019), SolarWinds (2020), "
                    "Uber (2022), Okta (2022) — in each one, an over-privileged identity was "
                    "the piece that unlocked the rest. Knowing IAM means knowing how to "
                    "survive this week's S3 leak."
                ),
                "body": (
                """<h3>1. Identidades: humanas vs máquina</h3>
<p>Duas categorias de identidade exigem tratamento estruturalmente
diferente. As <strong>humanas</strong> — dev, ops, financeiro, vendas —
acessam console e CLI, e devem ser federadas via SSO (IAM Identity
Center, Entra ID, Google Workspace) com MFA forte, idealmente hardware
key FIDO2, não SMS. As identidades <strong>de máquina</strong> (workload)
— aplicação, pipeline, agente — devem usar credencial TEMPORÁRIA por
padrão: role assumida via STS, IRSA no EKS, Workload Identity no GKE,
Managed Identity no Azure, OIDC no CI/CD. O anti-pattern grave é
inverter os dois papéis — um humano usando credencial de máquina
(chave estática de uma role) ou uma aplicação usando credencial humana
(a chave pessoal de um dev rodando direto em produção) — cada
identidade precisa do fluxo desenhado para o seu próprio tipo.</p>
<div class="mermaid">
flowchart TD
    A["Requisição chega"] --> B{"Identidade autenticada?"}
    B -- "Não" --> C["Nega acesso, 401"]
    B -- "Sim" --> D{"Política permite a ação no recurso?"}
    D -- "Não" --> E["Nega acesso, 403"]
    D -- "Sim" --> F["Permite a ação"]
</div>


<h3>2. Estrutura de uma policy IAM (AWS)</h3>
<p>Uma policy é um documento JSON declarativo:</p>
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReports",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::reports-prod",
        "arn:aws:s3:::reports-prod/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceVpc": "vpc-0abc123"
        },
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        },
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-01-01T00:00:00Z"
        }
      }
    }
  ]
}</code></pre>
<p>Cada Statement combina quatro peças: <code>Effect</code> declara
Allow ou Deny; <code>Action</code> lista as operações específicas
permitidas ou negadas (<code>s3:GetObject</code>,
<code>ec2:RunInstances</code>), onde wildcard exige cuidado redobrado
por abrir mais do que normalmente se pretende; <code>Resource</code>
especifica exatamente quais ARNs a regra afeta; e <code>Condition</code>
adiciona contexto opcional que restringe quando a regra se aplica de
fato.</p>

<h3>3. Avaliação: como o IAM decide</h3>
<p>O algoritmo de avaliação segue uma ordem específica que muda
completamente o resultado se mal entendida. Por padrão, TUDO é negado —
o modelo é opt-in, não opt-out. Uma SCP (a nível de Organizations)
restringe o universo do possível antes de qualquer outra coisa ser
avaliada: se a SCP nega, acabou ali mesmo, nem o administrador da conta
individual consegue contornar. Dentro do que a SCP permite, uma
resource policy (como bucket policy) ou uma identity policy explícita
com Allow concede o acesso. Mas QUALQUER Deny explícito, em qualquer
camada, sobrescreve qualquer Allow — não importa quantas policies
concedam acesso, um Deny explícito sempre vence. E permission boundaries
(aplicadas a usuário ou role) funcionam como um teto adicional por cima
de tudo isso. Resumindo em uma expressão: <code>SCP ∩ (Policy ∪
ResourcePolicy) ∩ Boundary − Deny</code>.</p>

<h3>4. Roles &gt; usuários, sempre</h3>
<table>
<tr><th></th><th>User</th><th>Role</th></tr>
<tr><td>Credencial</td><td>permanente (chave/senha)</td>
<td>temporária (~15min-12h via STS)</td></tr>
<tr><td>Quem usa</td><td>geralmente humano</td><td>qualquer principal
que assuma (humano, app, outra conta, OIDC)</td></tr>
<tr><td>Vazamento</td><td>vale para sempre até rotacionar</td>
<td>expira sozinha</td></tr>
<tr><td>Auditoria</td><td>'user X fez Y'</td>
<td>'user X assumiu role R e fez Y'</td></tr>
</table>
<p>A diferença mais crítica dessa tabela é a linha de vazamento: uma
chave de usuário roubada continua válida indefinidamente até alguém
perceber e rotacionar manualmente, enquanto uma credencial de role
expira sozinha em minutos ou horas — mesmo se roubada, o dano tem prazo
de validade embutido. Isso justifica a recomendação moderna de
<strong>zero usuários IAM</strong> em produção: tudo passa por
federação SSO para humano e role assumida para aplicação.</p>

<h3>5. CI/CD com OIDC, fim das chaves estáticas</h3>
<p>O anti-pattern clássico é armazenar uma access key da AWS como
secret no GitHub Actions ou GitLab CI — se vazar, vira uma porta de
entrada permanente em produção, sem data de expiração. O padrão
moderno, OIDC federation, resolve isso na raiz: o próprio provedor de
CI emite um JWT contendo claims verificáveis (repositório, branch,
workflow), e a AWS valida esse token e troca por credencial STS
temporária — nenhuma chave de longa duração jamais precisa existir:</p>
<pre><code># Trust policy da role (quem pode assumir)
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
      }
    }
  }]
}</code></pre>
<pre><code># GitHub Actions workflow
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/github-deploy
          aws-region: us-east-1
      - run: aws s3 sync ./dist s3://bucket/</code></pre>
<p>O <code>StringLike</code> restringindo o <code>sub</code> ao branch
<code>main</code> é o que impede qualquer outro branch ou fork de
assumir essa mesma role — sem essa condição, qualquer PR de qualquer
pessoa com acesso ao repositório poderia obter a mesma credencial.
Sem chave estática, não há rotação para esquecer e não há vazamento
crítico possível — o JWT em si vive apenas minutos.</p>

<h3>6. Hierarquia organizacional, guard-rails</h3>
<p>Em organização séria, conta AWS (ou subscription Azure, ou project
GCP) se organiza em árvore, não como uma lista plana:</p>
<pre><code>Root
├── OU Production
│   ├── account: prod-app-frontend
│   └── account: prod-app-backend
├── OU NonProd
│   ├── account: staging
│   └── account: dev
├── OU Sandbox
│   └── account: dev-experiments  (alta liberdade, isolada)
└── OU Security
    ├── account: log-archive  (CloudTrail centralizado)
    └── account: audit         (read-only para compliance)</code></pre>
<p>Uma SCP aplicada numa OU desce automaticamente para todas as contas
filhas, sem precisar repetir a regra em cada uma — algumas SCPs comuns
negam qualquer ação fora das regiões aprovadas, negam criação de IAM
user em conta de produção (forçando o modelo zero-usuário da seção 4),
negam desligar o CloudTrail (protegendo a própria auditoria de ser
apagada por um atacante) e negam criação de bucket sem encryption.</p>

<h3>7. Conditions: o segredo das policies poderosas</h3>
<p>Um conjunto de condition keys da AWS abre controle bem mais fino do
que Allow/Deny simples: <code>aws:MultiFactorAuthPresent</code> e
<code>aws:MultiFactorAuthAge</code> exigem MFA recente; <code>aws:SourceIp</code>
e <code>aws:VpcSourceIp</code> restringem por origem de rede;
<code>aws:SourceVpc</code> e <code>aws:SourceVpce</code> restringem por
VPC específica; <code>aws:RequestedRegion</code> restringe região;
<code>aws:CurrentTime</code> restringe janela de horário;
<code>aws:ResourceTag/&lt;tag&gt;</code> e
<code>aws:PrincipalTag/&lt;tag&gt;</code> habilitam ABAC; e
<code>aws:SecureTransport</code> força HTTPS. O ABAC
(Attribute-Based Access Control) muda o modelo mental de "uma role por
equipe" para tag em recurso e em principal: a policy passa a dizer
"usuário com <code>team=alpha</code> pode acessar recurso com
<code>team=alpha</code>" — uma única regra que escala automaticamente
conforme times e recursos novos surgem, sem precisar criar role nova
para cada combinação.</p>

<h3>8. Auditoria: CloudTrail, GuardDuty, Access Analyzer</h3>
<p>Quatro ferramentas cobrem auditoria em camadas complementares. O
<strong>CloudTrail</strong> registra toda chamada de API feita na
conta — o ideal é um trail org-wide encaminhando para um bucket numa
conta SEPARADA (log-archive) com object-lock ativado, porque sem esse
isolamento um atacante que comprometa a conta principal também apaga os
próprios logs que o denunciariam. O <strong>GuardDuty</strong> faz
detecção comportamental — API anômala, mineração de criptomoeda,
padrão de exfiltração — sinalizando o que foge do comportamento normal
esperado. O <strong>IAM Access Analyzer</strong> gera relatório do que
cada principal REALMENTE usou nos últimos 90 dias, permitindo podar
permissão concedida mas nunca exercida. E o <strong>Access
Advisor</strong> aponta diretamente "o serviço Y nunca foi acessado por
esta role" — um sinal direto do que remover sem risco.</p>

<h3>9. Azure Entra ID e GCP IAM, equivalentes</h3>
<p>No Azure, o <strong>Entra ID</strong> (antigo Azure AD) cuida da
identidade em si; o <strong>RBAC</strong> aplica roles built-in
(Reader, Contributor, Owner) ou custom, sempre em um escopo específico
(subscription, resource group ou resource individual); o
<strong>Conditional Access</strong> combina múltiplos fatores numa só
regra — "só permite login se MFA E device compliant E IP corporativo" —
granular o bastante para cobrir cenário real de política corporativa; e
o <strong>PIM</strong> (Privileged Identity Management) implementa
acesso just-in-time, onde o usuário "eleva" temporariamente para Owner
mediante aprovação explícita, em vez de manter privilégio elevado
permanentemente ativo. No GCP, o IAM usa bindings — membro, role e
recurso combinados — com roles predefinidas ou custom; a Resource
Hierarchy organiza Organization, Folders, Projects e Resources numa
árvore equivalente à das OUs da AWS; o Workload Identity substitui a
chave de service account pelo mesmo princípio de credencial temporária
da seção 1; e as Org Policies cumprem o papel de guard-rail
equivalente à SCP.</p>

<h3>10. Anti-patterns clássicos</h3>
<ul>
<li><strong>Conta root com chave estática em uso diário</strong>:
NUNCA — root deveria ficar trancado, usado só em emergência
extrema.</li>
<li><strong>Access key em <code>git push</code> público</strong>: vaza
em menos de uma hora, capturada por bot scanner automatizado.</li>
<li><strong>Role <code>AdministratorAccess</code> em app de
produção "porque estava dando erro"</strong>: resolve o sintoma
imediato e cria um risco permanente muito maior.</li>
<li><strong>Ninguém com MFA, ou MFA via SMS</strong>: vulnerável a SIM
swap — prefira FIDO2/hardware key (seção 1).</li>
<li><strong>Permission creep</strong>: todo mundo só adiciona
permissão, ninguém remove — o Access Analyzer (seção 8) existe
justamente para reverter essa tendência.</li>
<li><strong>Sem CloudTrail, ou CloudTrail numa única região</strong>:
deixa boa parte da atividade real sem registro nenhum.</li>
<li><strong>Mesma role usada por 50 aplicações diferentes</strong>
"porque é mais simples": qualquer uma comprometida herda o acesso de
todas as outras.</li>
<li><strong>Sem rotação de access key</strong>: uma chave estática
esquecida há anos é exatamente o tipo de coisa que ninguém lembra de
revogar.</li>
<li><strong>Senha sem complexidade ou sem rotação periódica</strong>:
abre a porta mais óbvia de força bruta.</li>
<li><strong>Compartilhamento de credencial entre humanos</strong> ("o
login do time"): elimina toda rastreabilidade de quem fez o quê.</li>
</ul>

<h3>11. Caso real: Uber 2022</h3>
<p>Um atacante comprou credencial de funcionário da Uber vazada na
dark web, e bombardeou notificação push de MFA repetidamente até o
funcionário aprovar só para fazer o alarme parar — um ataque conhecido
como MFA fatigue. Uma vez dentro da rede, o atacante encontrou um
script PowerShell num compartilhamento interno com credencial
HARD-CODED de uma conta de Privileged Access Management, e usou isso
para escalar até Vault, AWS, GCP e GSuite — um único script esquecido
destrancou praticamente tudo. As lições ficam claras à luz das seções
anteriores: MFA via SMS ou push simples é vulnerável exatamente a esse
tipo de fadiga (seção 1), e number matching ou hardware key teriam
quebrado esse ataque específico; credencial hard-coded em script
interno é uma bomba-relógio esperando ser encontrada; e uma conta de
PAM precisa estar isolada com MFA reforçado próprio, não tratada como
mais uma credencial comum na rede interna.</p>"""
                ),
                "body_en": (
                """<h3>1. Identities: human vs machine</h3>
<p>Two identity categories require structurally different treatment.
<strong>Human</strong> identities — dev, ops, finance, sales — access
the console and CLI, and should be federated via SSO (IAM Identity
Center, Entra ID, Google Workspace) with strong MFA, ideally a FIDO2
hardware key, not SMS. <strong>Machine</strong> (workload) identities
— application, pipeline, agent — should use TEMPORARY credentials by
default: a role assumed via STS, IRSA on EKS, Workload Identity on
GKE, Managed Identity on Azure, OIDC in CI/CD. The serious anti-pattern
is swapping the two roles — a human using a machine credential (a
role's static key) or an application using a human credential (a
dev's personal key running directly in production) — each identity
needs the flow designed for its own type.</p>
<div class="mermaid">
flowchart TD
    A["Requisição chega"] --> B{"Identidade autenticada?"}
    B -- "Não" --> C["Nega acesso, 401"]
    B -- "Sim" --> D{"Política permite a ação no recurso?"}
    D -- "Não" --> E["Nega acesso, 403"]
    D -- "Sim" --> F["Permite a ação"]
</div>


<h3>2. Structure of an IAM policy (AWS)</h3>
<p>A policy is a declarative JSON document:</p>
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReports",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::reports-prod",
        "arn:aws:s3:::reports-prod/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceVpc": "vpc-0abc123"
        },
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        },
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-01-01T00:00:00Z"
        }
      }
    }
  ]
}</code></pre>
<p>Each Statement combines four pieces: <code>Effect</code> declares
Allow or Deny; <code>Action</code> lists the specific operations
allowed or denied (<code>s3:GetObject</code>,
<code>ec2:RunInstances</code>), where a wildcard demands extra care
because it opens more than is normally intended; <code>Resource</code>
specifies exactly which ARNs the rule affects; and <code>Condition</code>
adds optional context that restricts when the rule actually applies.</p>

<h3>3. Evaluation: how IAM decides</h3>
<p>The evaluation algorithm follows a specific order that completely
changes the outcome if misunderstood. By default, EVERYTHING is
denied — the model is opt-in, not opt-out. An SCP (at the Organizations
level) restricts the universe of what's possible before anything else
is evaluated: if the SCP denies, it stops right there, and not even
the individual account's administrator can work around it. Within
what the SCP allows, a resource policy (like a bucket policy) or an
explicit identity policy with Allow grants access. But ANY explicit
Deny, at any layer, overrides any Allow — no matter how many policies
grant access, an explicit Deny always wins. And permission boundaries
(applied to a user or role) act as an additional ceiling on top of all
of this. Summed up in one expression: <code>SCP ∩ (Policy ∪
ResourcePolicy) ∩ Boundary − Deny</code>.</p>

<h3>4. Roles &gt; users, always</h3>
<table>
<tr><th></th><th>User</th><th>Role</th></tr>
<tr><td>Credential</td><td>permanent (key/password)</td>
<td>temporary (~15min-12h via STS)</td></tr>
<tr><td>Who uses it</td><td>usually human</td><td>any principal
that assumes it (human, app, another account, OIDC)</td></tr>
<tr><td>Leak</td><td>valid forever until rotated</td>
<td>expires on its own</td></tr>
<tr><td>Audit</td><td>'user X did Y'</td>
<td>'user X assumed role R and did Y'</td></tr>
</table>
<p>The most critical difference in this table is the leak row: a
stolen user key stays valid indefinitely until someone notices and
manually rotates it, while a role's credential expires on its own in
minutes or hours — even if stolen, the damage has a built-in
expiration date. This justifies the modern recommendation of
<strong>zero IAM users</strong> in production: everything goes through
SSO federation for humans and assumed roles for applications.</p>

<h3>5. CI/CD with OIDC, the end of static keys</h3>
<p>The classic anti-pattern is storing an AWS access key as a secret
in GitHub Actions or GitLab CI — if it leaks, it becomes a permanent
door into production, with no expiration date. The modern pattern,
OIDC federation, fixes this at the root: the CI provider itself issues
a JWT with verifiable claims (repository, branch, workflow), and AWS
validates that token and exchanges it for a temporary STS credential
— no long-lived key ever needs to exist:</p>
<pre><code># Trust policy da role (quem pode assumir)
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
      }
    }
  }]
}</code></pre>
<pre><code># GitHub Actions workflow
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/github-deploy
          aws-region: us-east-1
      - run: aws s3 sync ./dist s3://bucket/</code></pre>
<p>The <code>StringLike</code> restricting <code>sub</code> to the
<code>main</code> branch is what stops any other branch or fork from
assuming this same role — without that condition, any PR from anyone
with repository access could obtain the same credential. With no
static key, there's no rotation to forget and no critical leak
possible — the JWT itself lives only for minutes.</p>

<h3>6. Organizational hierarchy, guard-rails</h3>
<p>In a serious organization, the AWS account (or Azure subscription,
or GCP project) is organized as a tree, not a flat list:</p>
<pre><code>Root
├── OU Production
│   ├── account: prod-app-frontend
│   └── account: prod-app-backend
├── OU NonProd
│   ├── account: staging
│   └── account: dev
├── OU Sandbox
│   └── account: dev-experiments  (alta liberdade, isolada)
└── OU Security
    ├── account: log-archive  (CloudTrail centralizado)
    └── account: audit         (read-only para compliance)</code></pre>
<p>An SCP applied to an OU flows down automatically to every child
account, with no need to repeat the rule in each one — some common
SCPs deny any action outside approved regions, deny creating an IAM
user in a production account (enforcing the zero-user model from
section 4), deny disabling CloudTrail (protecting the audit trail
itself from being erased by an attacker), and deny creating a bucket
without encryption.</p>

<h3>7. Conditions: the secret of powerful policies</h3>
<p>A set of AWS condition keys opens up much finer control than plain
Allow/Deny: <code>aws:MultiFactorAuthPresent</code> and
<code>aws:MultiFactorAuthAge</code> require recent MFA;
<code>aws:SourceIp</code> and <code>aws:VpcSourceIp</code> restrict by
network origin; <code>aws:SourceVpc</code> and <code>aws:SourceVpce</code>
restrict by a specific VPC; <code>aws:RequestedRegion</code> restricts
region; <code>aws:CurrentTime</code> restricts a time window;
<code>aws:ResourceTag/&lt;tag&gt;</code> and
<code>aws:PrincipalTag/&lt;tag&gt;</code> enable ABAC; and
<code>aws:SecureTransport</code> forces HTTPS. ABAC (Attribute-Based
Access Control) shifts the mental model from "one role per team" to
tags on resource and principal: the policy now says "a user with
<code>team=alpha</code> can access a resource with
<code>team=alpha</code>" — a single rule that automatically scales as
new teams and resources appear, with no need to create a new role for
every combination.</p>

<h3>8. Auditing: CloudTrail, GuardDuty, Access Analyzer</h3>
<p>Four tools cover auditing in complementary layers.
<strong>CloudTrail</strong> logs every API call made in the account —
the ideal is an org-wide trail forwarding to a bucket in a SEPARATE
account (log-archive) with object-lock enabled, because without that
isolation an attacker who compromises the main account can also erase
the very logs that would expose them. <strong>GuardDuty</strong> does
behavioral detection — anomalous API calls, cryptocurrency mining,
exfiltration patterns — flagging what deviates from expected normal
behavior. <strong>IAM Access Analyzer</strong> generates a report of
what each principal ACTUALLY used over the last 90 days, letting you
prune permissions that were granted but never exercised. And
<strong>Access Advisor</strong> points directly at "service Y was
never accessed by this role" — a direct signal of what can be removed
without risk.</p>

<h3>9. Azure Entra ID and GCP IAM, equivalents</h3>
<p>On Azure, <strong>Entra ID</strong> (formerly Azure AD) handles the
identity itself; <strong>RBAC</strong> applies built-in roles (Reader,
Contributor, Owner) or custom ones, always at a specific scope
(subscription, resource group, or individual resource);
<strong>Conditional Access</strong> combines multiple factors into one
rule — "only allow login if MFA AND device compliant AND corporate
IP" — granular enough to cover a real corporate policy scenario; and
<strong>PIM</strong> (Privileged Identity Management) implements
just-in-time access, where the user "elevates" temporarily to Owner
through explicit approval, instead of keeping elevated privilege
permanently active. On GCP, IAM uses bindings — member, role, and
resource combined — with predefined or custom roles; the Resource
Hierarchy organizes Organization, Folders, Projects, and Resources
into a tree equivalent to AWS's OUs; Workload Identity replaces the
service account key with the same temporary-credential principle from
section 1; and Org Policies play the guard-rail role equivalent to an
SCP.</p>

<h3>10. Classic anti-patterns</h3>
<ul>
<li><strong>Root account with a static key in daily use</strong>:
NEVER — root should stay locked away, used only in extreme
emergencies.</li>
<li><strong>Access key in a public <code>git push</code></strong>:
leaks in under an hour, captured by an automated scanner bot.</li>
<li><strong><code>AdministratorAccess</code> role on a production
app "because it kept erroring"</strong>: fixes the immediate symptom
and creates a much bigger permanent risk.</li>
<li><strong>Nobody has MFA, or MFA is via SMS</strong>: vulnerable to
SIM swap — prefer FIDO2/hardware key (section 1).</li>
<li><strong>Permission creep</strong>: everyone only adds permission,
nobody removes it — Access Analyzer (section 8) exists precisely to
reverse this tendency.</li>
<li><strong>No CloudTrail, or CloudTrail in a single region</strong>:
leaves a good chunk of real activity completely unlogged.</li>
<li><strong>The same role used by 50 different applications</strong>
"because it's simpler": if any one of them is compromised, it
inherits the access of all the others.</li>
<li><strong>No access key rotation</strong>: a static key forgotten
for years is exactly the kind of thing nobody remembers to
revoke.</li>
<li><strong>Passwords with no complexity or periodic rotation</strong>:
opens the most obvious brute-force door.</li>
<li><strong>Sharing a credential between humans</strong> ("the team's
login"): eliminates all traceability of who did what.</li>
</ul>

<h3>11. Real case: Uber 2022</h3>
<p>An attacker bought a leaked Uber employee credential on the dark
web, then bombarded the employee with repeated MFA push notifications
until they approved one just to make the alarm stop — an attack known
as MFA fatigue. Once inside the network, the attacker found a
PowerShell script on an internal share with a HARD-CODED credential
for a Privileged Access Management account, and used it to escalate
into Vault, AWS, GCP, and GSuite — a single forgotten script unlocked
practically everything. The lessons are clear in light of the earlier
sections: MFA via SMS or simple push is vulnerable to exactly this
kind of fatigue (section 1), and number matching or a hardware key
would have broken this specific attack; a hard-coded credential in an
internal script is a ticking time bomb waiting to be found; and a PAM
account needs to be isolated with its own reinforced MFA, not treated
as just another ordinary credential on the internal network.</p>"""
                ),
                "practical": (
                    "(1) Crie uma role IAM <code>read-reports</code> que pode apenas "
                    "<code>s3:GetObject</code> e <code>s3:ListBucket</code> em "
                    "<code>arn:aws:s3:::meu-bucket</code> e <code>/*</code>, com "
                    "<code>Condition</code> exigindo MFA "
                    "(<code>aws:MultiFactorAuthPresent: true</code>).<br>"
                    "(2) Teste com IAM Policy Simulator em modo MFA-true e MFA-false; veja "
                    "as duas respostas.<br>"
                    "(3) Configure OIDC entre GitHub Actions e AWS, siga "
                    "<a href='https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services'>"
                    "doc oficial</a>. Faça deploy de um arquivo para S3 sem nenhuma chave "
                    "estática no GitHub.<br>"
                    "(4) Em <code>Access Analyzer → Generate Policy</code>, gere policy "
                    "baseada em uso histórico de uma role existente; compare com a policy "
                    "atual para encontrar permissões não usadas.<br>"
                    "(5) Bônus: monte uma SCP que negue criação de bucket S3 sem "
                    "encryption. Aplique em uma OU de testes."
                ),
                "practical_en": (
                    "(1) Create an IAM role <code>read-reports</code> that can only "
                    "<code>s3:GetObject</code> and <code>s3:ListBucket</code> on "
                    "<code>arn:aws:s3:::my-bucket</code> and <code>/*</code>, with a "
                    "<code>Condition</code> requiring MFA "
                    "(<code>aws:MultiFactorAuthPresent: true</code>).<br>"
                    "(2) Test with IAM Policy Simulator in MFA-true and MFA-false mode; "
                    "compare the two responses.<br>"
                    "(3) Set up OIDC between GitHub Actions and AWS, following the "
                    "<a href='https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services'>"
                    "official docs</a>. Deploy a file to S3 with no static key at all "
                    "in GitHub.<br>"
                    "(4) In <code>Access Analyzer → Generate Policy</code>, generate a "
                    "policy based on the historical usage of an existing role; compare it "
                    "with the current policy to find unused permissions.<br>"
                    "(5) Bonus: build an SCP that denies creating an S3 bucket without "
                    "encryption. Apply it to a test OU."
                ),
            },
            "materials": [
                m("AWS IAM Best Practices",
                  "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
                  "docs", "",
                  title_en="AWS IAM Best Practices",
                  description_en=""),
                m("Azure RBAC overview",
                  "https://learn.microsoft.com/azure/role-based-access-control/overview",
                  "docs", "",
                  title_en="Azure RBAC overview",
                  description_en=""),
                m("GCP IAM overview",
                  "https://cloud.google.com/iam/docs/overview", "docs", "",
                  title_en="GCP IAM overview",
                  description_en=""),
                m("Cloudonaut: IAM tutorials",
                  "https://cloudonaut.io/", "article", "",
                  title_en="Cloudonaut: IAM tutorials",
                  description_en=""),
                m("AWS Policy Simulator",
                  "https://policysim.aws.amazon.com/", "tool", "",
                  title_en="AWS Policy Simulator",
                  description_en=""),
                m("GitHub OIDC for AWS",
                  "https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services",
                  "docs", "Substituir chave estática por OIDC.",
                  title_en="GitHub OIDC for AWS",
                  description_en="Replace a static key with OIDC."),
            ],
            "questions": [
                q("Vantagem de role sobre chave estática:",
                  "Credenciais temporárias, sem armazenamento persistente.",
                  ["Custa menos, porque cobra por hora em vez de mensalidade fixa.",
                   "Cota maior de requisição por segundo concedida a esse tipo de credencial.",
                   "Handshake mais rápido do que o de uma credencial estática comum."],
                  "Chave temporária expira sozinha; chave estática vaza e fica em open-source forever.",
                  statement_en="Advantage of a role over a static key:",
                  correct_en="Temporary credentials, with no persistent storage.",
                  wrong_en=["Costs less, because it charges hourly instead of a fixed monthly fee.",
                            "Higher per-second request quota granted to this type of credential.",
                            "Faster handshake than a typical static credential provides."],
                  explanation_en="A temporary credential expires on its own; a static key leaks and stays valid in open-source forever."),
                q("MFA serve para:",
                  "Adicionar segundo fator (algo que você tem) à autenticação.",
                  ["Substitui a senha por completo, eliminando a etapa de digitá-la.",
                   "Aumenta a cota de requisição disponível para aquele usuário específico.",
                   "Gera um token de DNS usado para provar propriedade de domínio."],
                  "Reduz drasticamente o risco de credential stuffing, mesmo se a senha vaza, MFA segura.",
                  statement_en="MFA exists to:",
                  correct_en="Add a second factor (something you have) to authentication.",
                  wrong_en=["Completely replaces the password, eliminating the step of typing it.",
                            "Increases the request quota available to that specific user.",
                            "Generates a DNS token used to prove domain ownership."],
                  explanation_en="Drastically reduces credential-stuffing risk, since even if the password leaks, MFA still protects the account."),
                q("Policy IAM é avaliada como:",
                  "Combinação de Allow/Deny, Deny sempre vence em conflito.",
                  ["A última regra escrita no arquivo de política vence sobre as demais.",
                   "Considera só o Allow mais recente adicionado à política do usuário.",
                   "Escolhida de forma aleatória entre as regras aplicáveis ao caso, sem critério fixo."],
                  "Sem Allow explícito, default é negar. Deny sempre wins, mesmo se houver Allow em outra policy.",
                  statement_en="An IAM policy is evaluated as:",
                  correct_en="A combination of Allow/Deny, where an explicit Deny always wins.",
                  wrong_en=["The last rule written in the policy file overrides every other rule.",
                            "Only considers the most recently added Allow in the user's policy.",
                            "Chosen at random among the applicable rules, with no fixed criteria."],
                  explanation_en="With no explicit Allow, the default is to deny. Deny always wins, even if an Allow exists in another policy."),
                q("Para devs sem precisar de console, prefira:",
                  "Roles e federação (IAM Identity Center / SSO).",
                  ["Usuário do IAM com uma chave de acesso de longa duração.",
                   "Compartilhar a mesma credencial entre vários desenvolvedores do time.",
                   "Senha enviada por SMS a cada tentativa de login do usuário."],
                  "Acesso temporário emitido por SSO; nada de chave longa flutuando em ~/.aws/credentials.",
                  statement_en="For devs who don't need console access, prefer:",
                  correct_en="Should always use roles and federation (IAM Identity Center / SSO).",
                  wrong_en=["An IAM user with a long-lived access key issued once and rarely rotated.",
                            "Sharing the same credential among several developers on the team.",
                            "A password sent via SMS on every login attempt by the user."],
                  explanation_en="Temporary access issued by SSO; no long-lived key floating around in ~/.aws/credentials."),
                q("SCP em AWS Organizations serve para:",
                  "Criar guardrails que limitam o que contas filhas podem fazer.",
                  ["Substituir a VPC inteira da conta por uma rede gerenciada completamente diferente.",
                   "Acelerar o tempo de deploy de uma aplicação específica dentro da conta.",
                   "Aumentar o valor total cobrado mensalmente na fatura consolidada da conta."],
                  "SCP é teto: mesmo Admin de uma sub-conta não escapa. Útil para impor compliance.",
                  statement_en="An SCP in AWS Organizations is used to:",
                  correct_en="Creating guardrails that always limit what child accounts can do.",
                  wrong_en=["Replacing the account's entire VPC with a completely different managed network.",
                            "Speeding up the deploy time of every application inside the account, without exception.",
                            "Increasing the total amount billed monthly on the account's consolidated invoice."],
                  explanation_en="An SCP is a ceiling: even a sub-account's Admin can't escape it. Useful for enforcing compliance."),
                q("Por que rotacionar access keys?",
                  "Limita o impacto se uma chave vazar.",
                  ["Reduz o custo mensal pago pelo uso da credencial na conta.",
                   "Necessário para o protocolo HTTPS funcionar corretamente na API.",
                   "Aumenta a velocidade de resposta da chamada de API feita."],
                  "Janela de exploração de uma chave vazada é o tempo entre vazamento e próxima rotação.",
                  statement_en="Why rotate access keys?",
                  correct_en="Limits the impact if a key ever leaks.",
                  wrong_en=["Reduces the monthly cost paid for using the credential on the account.",
                            "Required for the HTTPS protocol to work correctly with the API.",
                            "Increases the response speed of the API call being made."],
                  explanation_en="The exploitation window of a leaked key is the time between the leak and the next rotation."),
                q("Como aplicar PoLP em IAM?",
                  "Conceder apenas as ações e recursos estritamente necessários.",
                  ["Ignorar a política existente e criar uma nova do zero.",
                   "Permitir tudo logo no início e restringir depois aos poucos.",
                   "Conceder AdministratorAccess de saída para simplificar o setup."],
                  "Comece restrito; relaxe só se a app realmente precisar. Use Access Analyzer para encontrar excessos.",
                  statement_en="How do you apply PoLP (Principle of Least Privilege) in IAM?",
                  correct_en="Granting only the actions and resources strictly required.",
                  wrong_en=["Ignoring the existing policy and creating a brand-new one from scratch.",
                            "Allowing every permission at the start and gradually restricting them later.",
                            "Granting AdministratorAccess from day one to simplify the setup."],
                  explanation_en="Start restricted; relax only if the app truly needs it. Use Access Analyzer to find excess permissions."),
                q("Qual recurso registra quem fez o quê na AWS?",
                  "AWS CloudTrail.",
                  ["Athena, usado para consultar dado já armazenado, não para gerar log.",
                   "VPC Flow Logs, que registra tráfego de rede, não chamada de API.",
                   "Log do S3 sozinho, que cobre só aquele bucket específico."],
                  "CloudTrail registra calls de API. Habilitar org-wide trail e enviar para bucket protegido.",
                  statement_en="Which resource logs who did what in AWS?",
                  correct_en="AWS CloudTrail, which never skips a call once enabled.",
                  wrong_en=["Athena, used to query data already stored, not to generate logs.",
                            "VPC Flow Logs, which record network traffic, not API calls.",
                            "S3 logging alone, which only covers that one specific bucket."],
                  explanation_en="CloudTrail logs API calls. Enable an org-wide trail and send it to a protected bucket."),
                q("Diferença entre user e role:",
                  "User tem credenciais permanentes; role é assumida temporariamente.",
                  ["Um usuário só pode ser usado por pessoa humana, jamais por máquina automatizada.",
                   "Assumir uma role custa mais caro do que manter um usuário fixo.",
                   "Uma role está reservada só para máquina, sem uso possível por humano."],
                  "Humano pode assumir role via SSO; máquina via STS AssumeRole. Ambos podem.",
                  statement_en="Difference between a user and a role:",
                  correct_en="A user's credential is always permanent; a role is assumed temporarily.",
                  wrong_en=["A user can only ever be used by a human, never by an automated machine.",
                            "Assuming a role costs more than keeping a fixed user around, in most setups.",
                            "A role is reserved only for machines, with no possible use by a human."],
                  explanation_en="A human can assume a role via SSO; a machine via STS AssumeRole. Both are possible."),
                q("Recomendação para conta root:",
                  "Não usar para tarefas diárias e ativar MFA forte.",
                  ["Desativar completamente o MFA para agilizar o acesso diário.",
                   "Compartilhar a senha da conta root com o time de operação inteiro.",
                   "Usar a conta root para qualquer tarefa do dia a dia, sem restrição."],
                  "Use root só para tarefas que exigem (alterar conta, fechar). MFA hardware ideal.",
                  statement_en="Recommendation for the root account:",
                  correct_en="Never using it for daily tasks and always enabling strong MFA.",
                  wrong_en=["Turning off MFA completely to speed up the daily login flow.",
                            "Sharing the root account password with the entire operations team.",
                            "Always using the root account for any everyday task, without restriction."],
                  explanation_en="Use root only for tasks that require it (changing the account, closing it). A hardware MFA key is ideal."),
            ],
        },
        # =====================================================================
        # 2.4 VPC & Subnets
        # =====================================================================
        {
            "title": "VPC & Subnets",
            "title_en": "VPC & Subnets",
            "summary": "Criar seu próprio 'pedaço' de rede isolado na nuvem.",
            "summary_en": "Building your own isolated 'slice' of network in the cloud.",
            "lesson": {
                "intro": (
                    "VPC (Virtual Private Cloud) é o equivalente cloud das redes privadas que "
                    "você aprendeu na Fase 1. Tudo o que viu de TCP/IP, CIDR, subnets, "
                    "roteamento, NAT, firewall, vale aqui, com algumas diferenças importantes: "
                    "tudo é configurável por API em segundos, redundância vem de fábrica, e "
                    "decisões de design ficam fixadas porque mudar CIDR de uma VPC produtiva "
                    "é doloroso.<br><br>"
                    "Esta aula é Cisco para cloud: planejamento de IP, design multi-AZ, "
                    "padrões de conectividade (peering, TGW, VPN, endpoints), e os bugs "
                    "caros que pegam quem confia no default."
                ),
                "intro_en": (
                    "A VPC (Virtual Private Cloud) is the cloud equivalent of the private "
                    "networks you learned about in Phase 1. Everything you saw about "
                    "TCP/IP, CIDR, subnets, routing, NAT, firewalls, still applies here, "
                    "with a few important differences: everything is configurable via API "
                    "in seconds, redundancy comes built-in, and design decisions become "
                    "fixed because changing the CIDR of a production VPC is painful.<br><br>"
                    "This lesson is Cisco for the cloud: IP planning, multi-AZ design, "
                    "connectivity patterns (peering, TGW, VPN, endpoints), and the "
                    "expensive bugs that catch anyone who trusts the default."
                ),
                "body": (
                """<h3>1. Anatomia de uma VPC</h3>
<p>Uma VPC é uma rede privada virtual com um CIDR principal (por
exemplo <code>10.0.0.0/16</code>, oferecendo 65 mil IPs), podendo
receber até cinco CIDRs secundários adicionais quando o principal fica
pequeno demais. Ela existe dentro de uma única região, mas cobre todas
as zonas de disponibilidade (AZs) dessa região, e vem isolada por
padrão — sem rota para internet, sem rota para outra VPC, até que
alguém configure explicitamente. Dentro dela, seis peças compõem a
rede: <strong>subnets</strong> (blocos CIDR menores, cada um confinado
a uma única AZ), <strong>route tables</strong> (decidem para onde cada
pacote vai), o <strong>Internet Gateway</strong> (dá conectividade
pública), o <strong>NAT Gateway</strong> (dá saída privada para
internet sem expor entrada), <strong>Security Groups e NACLs</strong>
(filtros de tráfego, detalhados na próxima aula), e os
<strong>VPC Endpoints</strong> (acesso privado a serviço do próprio
provedor de nuvem, sem passar pela internet pública).</p>
<div class="mermaid">
flowchart TD
    VPC["VPC, 10.0.0.0/16"] --> Pub["Subnet pública, 10.0.1.0/24"]
    VPC --> Priv["Subnet privada, 10.0.2.0/24"]
    Pub --> IGW["Internet Gateway"]
    Priv --> NAT["NAT Gateway"]
    NAT --> IGW
</div>


<h3>2. Planejamento de IP, pense agora, sofra menos depois</h3>
<p>Mudar o CIDR de uma VPC já em produção é doloroso o bastante para
justificar planejar com folga desde o início. Uma VPC inteira em
<code>/16</code> (65 mil IPs) é o padrão razoável para a maioria dos
casos; uma subnet em <code>/24</code> (256 IPs) atende aplicação
pequena, enquanto <code>/22</code> (1024 IPs) atende aplicação grande —
um cluster Kubernetes, por exemplo, consome IP muito mais rápido do que
parece à primeira vista. Reservar faixas separadas para produção,
staging e dev evita conflito quando um peering entre elas se tornar
necessário no futuro. E vale evitar especificamente os ranges mais
populares — <code>10.0.0.0/16</code>, <code>172.31.0.0/16</code>
(default da AWS), <code>192.168.1.0/24</code> — porque são exatamente
os candidatos mais prováveis a colidir com uma VPN, um ambiente
on-premise ou outra VPC que alguém vá querer conectar depois:</p>
<pre><code>10.0.0.0/8       - todo o universo corporativo
  10.0.0.0/12  - prod   (10.0.0.0  - 10.15.255.255)
  10.16.0.0/12 - staging
  10.32.0.0/12 - dev
  10.48.0.0/12 - sandbox
Cada VPC: /16 dentro do bloco apropriado
Cada subnet: /22 ou /24 dentro da VPC</code></pre>

<h3>3. Subnets pública e privada</h3>
<p>A diferença entre os três tipos de subnet é PURAMENTE de
roteamento, não de configuração especial na própria subnet. Uma subnet
<strong>pública</strong> tem rota <code>0.0.0.0/0 → IGW</code> na sua
route table — qualquer recurso com IP público ali recebe internet
direta. Uma <strong>privada</strong> tem rota <code>0.0.0.0/0 → NAT
Gateway</code> — consegue SAIR para internet, mas ninguém de fora
consegue iniciar conexão de entrada. E uma <strong>isolada</strong>
não tem rota alguma para internet — a única saída possível é via VPC
Endpoint, para serviços como S3 ou DynamoDB. O padrão "three-tier"
clássico combina os três:</p>
<pre><code>VPC 10.0.0.0/16
├── Public  10.0.1.0/24  (AZ a)  - ALB
├── Public  10.0.2.0/24  (AZ b)  - ALB
├── Private 10.0.10.0/24 (AZ a)  - app servers
├── Private 10.0.11.0/24 (AZ b)  - app servers
├── Isolated 10.0.20.0/24 (AZ a) - RDS
└── Isolated 10.0.21.0/24 (AZ b) - RDS</code></pre>
<p>O load balancer recebe tráfego da internet, fala com a aplicação na
subnet privada, e a aplicação fala com o banco na subnet isolada — o
banco nunca toca a internet em nenhum ponto desse caminho.</p>

<h3>4. NAT Gateway, útil mas caro</h3>
<p>O NAT Gateway permite que subnet privada tenha saída para internet,
mas o custo na AWS soma duas parcelas: cerca de US$ 32 por mês só de
existir, mais US$ 0,045 por GB processado — e como alta disponibilidade
exige um NAT Gateway por AZ, esse custo se multiplica pelo número de
zonas usadas. Em aplicação que baixa muitos gigabytes de pacote, essa
conta domina a fatura de rede inteira. Quatro mitigações reduzem esse
custo: VPC Endpoints para S3 e DynamoDB tiram esse tráfego específico
do caminho do NAT completamente (seção 6); um mirror interno de
pacote (Artifactory, ECR) evita baixar o mesmo artefato repetidamente
de fora; NAT instances customizadas podem sair mais baratas em volume
muito alto; e um único NAT Gateway compartilhado em ambiente não-prod
troca alta disponibilidade por economia, aceitável fora de
produção.</p>

<h3>5. Conectividade VPC ↔ VPC ↔ on-prem</h3>
<table>
<tr><th>Opção</th><th>Caso de uso</th><th>Limite</th></tr>
<tr><td>VPC Peering</td><td>Conectar 2 VPCs com IPs distintos</td>
<td>1:1, sem trânsito (não 'roteia' entre peerings)</td></tr>
<tr><td>Transit Gateway</td><td>Hub-and-spoke para muitas VPCs e
on-prem</td><td>Custo por hora + por GB</td></tr>
<tr><td>VPN Site-to-Site</td><td>Conectar on-prem via internet
(IPsec)</td><td>Latência variável, ~1 Gbps</td></tr>
<tr><td>Direct Connect</td><td>Linha dedicada para on-prem</td>
<td>Caro, latência baixa, alta banda (até 100 Gbps)</td></tr>
<tr><td>VPC Endpoint (Gateway)</td><td>Acesso privado a S3/DynamoDB</td>
<td>Só esses dois serviços; gratuito</td></tr>
<tr><td>VPC Endpoint (Interface)</td>
<td>Acesso privado a outros serviços via PrivateLink</td>
<td>~US$ 7/mês por endpoint por AZ</td></tr>
<tr><td>PrivateLink</td><td>Expor seu serviço para outras contas
privadamente</td><td>Sem trânsito; 1:1</td></tr>
</table>
<p>A linha mais fácil de esquecer nessa tabela é a limitação de
trânsito do VPC Peering: A conectado a B, e B conectado a C, NÃO
significa que A alcança C automaticamente — cada peering é estritamente
ponto a ponto. Quando a topologia cresce além de algumas VPCs, o
Transit Gateway resolve isso como hub central.</p>

<h3>6. VPC Endpoints, economia e segurança</h3>
<p>Sem endpoint, uma EC2 numa subnet privada que chama S3 manda o
tráfego pela internet via NAT Gateway — ida e volta, com o custo por GB
da seção 4 incluído. Com endpoint, o mesmo tráfego nunca sai da rede
interna da AWS: fica mais barato (sem passar pelo NAT) e mais seguro
(nunca trafega pela internet pública):</p>
<pre><code>resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  policy = jsonencode({
    Statement = [{
      Effect = "Allow",
      Principal = "*",
      Action = ["s3:GetObject", "s3:PutObject"],
      Resource = [
        "arn:aws:s3:::meus-buckets/*"
      ]
    }]
  })
}</code></pre>
<p>A policy do próprio endpoint pode restringir qual bucket é acessível
por ali, de forma independente da policy IAM — se o endpoint nega, o
acesso fica negado mesmo que a policy IAM permitisse, uma camada
adicional de controle no caminho da rede.</p>

<h3>7. VPC Flow Logs, auditoria</h3>
<p>Registra metadado — nunca o payload em si — de cada pacote passando
por uma interface de rede (ENI):</p>
<pre><code>resource "aws_flow_log" "main" {
  log_destination = aws_s3_bucket.flow_logs.arn
  log_destination_type = "s3"
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}</code></pre>
<p>Esse registro serve para quatro usos distintos: investigar "por que
esse Security Group está bloqueando" olhando diretamente os REJECT
registrados; detectar exfiltração observando um volume de saída fora do
padrão esperado; atender exigência de compliance (PCI, por exemplo,
exige log de tráfego de rede); e fazer análise de custo, revelando
exatamente quem fala com quem dentro da infraestrutura.</p>

<h3>8. Limitações e armadilhas</h3>
<p>Um CIDR não pode se sobrepor entre VPCs que algum dia vão se
conectar via peering ou Transit Gateway — descobrir esse conflito seis
meses depois de ambas já estarem em produção transforma uma decisão de
planejamento em uma migração dolorosa e arriscada. A AWS reserva 5 IPs
em toda subnet (endereço de rede, router, DNS, um reservado para uso
futuro, e o broadcast), o que significa que uma subnet <code>/28</code>
nominalmente com 16 endereços entrega apenas 11 utilizáveis de fato.
Uma subnet existe em exatamente UMA AZ — alta disponibilidade exige, no
mínimo, duas subnets em AZs diferentes por camada da arquitetura. A
VPC default vem com configuração insegura por padrão, e deveria ser
apagada (ou pelo menos nunca usada) em conta de produção. E, como já
visto na seção 5, VPC peering não é transitivo — encadear peerings
esperando trânsito automático é um erro comum que só aparece quando
alguém tenta de fato alcançar a terceira ponta.</p>

<h3>9. Segurança em camadas</h3>
<p>Defesa em profundidade a nível de rede empilha seis camadas
sucessivas, cada uma assumindo que a anterior PODE falhar: uma VPC
dedicada para dado especialmente sensível (escopo PCI, por exemplo);
uma subnet isolada para o banco, sem rota nenhuma para internet; uma
NACL fazendo bloqueio amplo por subnet inteira; um Security Group
aplicando regra fina por instância individual; um firewall de host
(ufw, nftables) como rede de segurança adicional mesmo dentro da
própria máquina; e por fim a própria aplicação com WAF, autenticação e
autorização. Nenhuma camada isolada deveria ser a única linha de
defesa.</p>

<h3>10. Caso real: o NAT Gateway de US$ 80k</h3>
<p>Em 2022, uma startup relatou publicamente uma conta de US$ 80 mil
num único mês, inteiramente de NAT Gateway — o pipeline de machine
learning baixava modelo do Hugging Face hospedado em S3 público,
saindo pelo NAT e voltando pela internet num percurso desnecessariamente
longo. A solução combinou cache local com um VPC Endpoint para S3
(possível justamente porque a imagem do Hugging Face é hospedada lá), e
a conta caiu para cerca de US$ 200 por mês. A lição prática direta da
seção 4: cada gigabyte de egress via NAT Gateway custa US$ 0,045 — em
escala, isso soma rápido o suficiente para virar a maior linha da
fatura sem que ninguém perceba a tempo.</p>"""
                ),
                "body_en": (
                """<h3>1. Anatomy of a VPC</h3>
<p>A VPC is a virtual private network with a primary CIDR (for
example <code>10.0.0.0/16</code>, offering 65 thousand IPs), able to
receive up to five additional secondary CIDRs when the primary one
becomes too small. It exists within a single region, but spans every
availability zone (AZ) in that region, and comes isolated by default
— no route to the internet, no route to another VPC, until someone
explicitly configures one. Inside it, six pieces make up the network:
<strong>subnets</strong> (smaller CIDR blocks, each confined to a
single AZ), <strong>route tables</strong> (decide where each packet
goes), the <strong>Internet Gateway</strong> (provides public
connectivity), the <strong>NAT Gateway</strong> (provides private
outbound access to the internet without exposing inbound access),
<strong>Security Groups and NACLs</strong> (traffic filters, covered
in the next lesson), and <strong>VPC Endpoints</strong> (private
access to a cloud provider's own service, without going over the
public internet).</p>
<div class="mermaid">
flowchart TD
    VPC["VPC, 10.0.0.0/16"] --> Pub["Subnet pública, 10.0.1.0/24"]
    VPC --> Priv["Subnet privada, 10.0.2.0/24"]
    Pub --> IGW["Internet Gateway"]
    Priv --> NAT["NAT Gateway"]
    NAT --> IGW
</div>


<h3>2. IP planning, think now, suffer less later</h3>
<p>Changing the CIDR of a VPC already in production is painful enough
to justify planning with plenty of room from the start. A whole VPC
as a <code>/16</code> (65 thousand IPs) is a reasonable default for
most cases; a subnet as a <code>/24</code> (256 IPs) covers a small
application, while a <code>/22</code> (1024 IPs) covers a large one —
a Kubernetes cluster, for instance, burns through IPs far faster than
it first appears. Reserving separate ranges for production, staging,
and dev avoids conflicts once peering between them becomes necessary
down the road. And it's worth specifically avoiding the most popular
ranges — <code>10.0.0.0/16</code>, <code>172.31.0.0/16</code> (AWS's
default), <code>192.168.1.0/24</code> — because they are exactly the
most likely candidates to collide with a VPN, an on-premise
environment, or another VPC someone will want to connect later:</p>
<pre><code>10.0.0.0/8       - todo o universo corporativo
  10.0.0.0/12  - prod   (10.0.0.0  - 10.15.255.255)
  10.16.0.0/12 - staging
  10.32.0.0/12 - dev
  10.48.0.0/12 - sandbox
Cada VPC: /16 dentro do bloco apropriado
Cada subnet: /22 ou /24 dentro da VPC</code></pre>

<h3>3. Public and private subnets</h3>
<p>The difference between the three subnet types is PURELY about
routing, not any special configuration on the subnet itself. A
<strong>public</strong> subnet has the route <code>0.0.0.0/0 → IGW</code>
in its route table — any resource with a public IP there gets direct
internet access. A <strong>private</strong> one has the route
<code>0.0.0.0/0 → NAT Gateway</code> — it can reach OUT to the
internet, but nobody outside can initiate an inbound connection. And
an <strong>isolated</strong> one has no route to the internet at all
— the only way out is via a VPC Endpoint, for services like S3 or
DynamoDB. The classic "three-tier" pattern combines all three:</p>
<pre><code>VPC 10.0.0.0/16
├── Public  10.0.1.0/24  (AZ a)  - ALB
├── Public  10.0.2.0/24  (AZ b)  - ALB
├── Private 10.0.10.0/24 (AZ a)  - app servers
├── Private 10.0.11.0/24 (AZ b)  - app servers
├── Isolated 10.0.20.0/24 (AZ a) - RDS
└── Isolated 10.0.21.0/24 (AZ b) - RDS</code></pre>
<p>The load balancer receives traffic from the internet, talks to the
application in the private subnet, and the application talks to the
database in the isolated subnet — the database never touches the
internet at any point along that path.</p>

<h3>4. NAT Gateway, useful but expensive</h3>
<p>The NAT Gateway lets a private subnet reach the internet, but the
cost on AWS adds up in two parts: roughly $32 a month just for
existing, plus $0.045 per GB processed — and since high availability
requires one NAT Gateway per AZ, that cost multiplies by the number
of zones in use. For an application that downloads a lot of
gigabytes, this bill can dominate the entire network invoice. Four
mitigations reduce this cost: VPC Endpoints for S3 and DynamoDB take
that specific traffic out of the NAT path entirely (section 6); an
internal package mirror (Artifactory, ECR) avoids repeatedly
downloading the same artifact from outside; custom NAT instances can
work out cheaper at very high volume; and a single shared NAT Gateway
in a non-prod environment trades high availability for savings,
acceptable outside of production.</p>

<h3>5. Connectivity VPC ↔ VPC ↔ on-prem</h3>
<table>
<tr><th>Opção</th><th>Caso de uso</th><th>Limite</th></tr>
<tr><td>VPC Peering</td><td>Conectar 2 VPCs com IPs distintos</td>
<td>1:1, sem trânsito (não 'roteia' entre peerings)</td></tr>
<tr><td>Transit Gateway</td><td>Hub-and-spoke para muitas VPCs e
on-prem</td><td>Custo por hora + por GB</td></tr>
<tr><td>VPN Site-to-Site</td><td>Conectar on-prem via internet
(IPsec)</td><td>Latência variável, ~1 Gbps</td></tr>
<tr><td>Direct Connect</td><td>Linha dedicada para on-prem</td>
<td>Caro, latência baixa, alta banda (até 100 Gbps)</td></tr>
<tr><td>VPC Endpoint (Gateway)</td><td>Acesso privado a S3/DynamoDB</td>
<td>Só esses dois serviços; gratuito</td></tr>
<tr><td>VPC Endpoint (Interface)</td>
<td>Acesso privado a outros serviços via PrivateLink</td>
<td>~US$ 7/mês por endpoint por AZ</td></tr>
<tr><td>PrivateLink</td><td>Expor seu serviço para outras contas
privadamente</td><td>Sem trânsito; 1:1</td></tr>
</table>
<p>The easiest thing to forget in this table is VPC Peering's transit
limitation: A connected to B, and B connected to C, does NOT mean
that A automatically reaches C — each peering connection is strictly
point-to-point. Once the topology grows beyond a few VPCs, the
Transit Gateway solves this by acting as a central hub.</p>

<h3>6. VPC Endpoints, savings and security</h3>
<p>Without an endpoint, an EC2 instance in a private subnet calling
S3 sends that traffic over the internet via the NAT Gateway — round
trip, including the per-GB cost from section 4. With an endpoint,
that same traffic never leaves AWS's internal network: it's cheaper
(bypassing the NAT) and more secure (never traveling over the public
internet):</p>
<pre><code>resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  policy = jsonencode({
    Statement = [{
      Effect = "Allow",
      Principal = "*",
      Action = ["s3:GetObject", "s3:PutObject"],
      Resource = [
        "arn:aws:s3:::meus-buckets/*"
      ]
    }]
  })
}</code></pre>
<p>The endpoint's own policy can restrict which bucket is accessible
through it, independently of the IAM policy — if the endpoint denies
it, access is denied even if the IAM policy would have allowed it, an
additional layer of control at the network level.</p>

<h3>7. VPC Flow Logs, auditing</h3>
<p>Records metadata — never the payload itself — for every packet
passing through a network interface (ENI):</p>
<pre><code>resource "aws_flow_log" "main" {
  log_destination = aws_s3_bucket.flow_logs.arn
  log_destination_type = "s3"
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}</code></pre>
<p>This record serves four distinct purposes: investigating "why is
this Security Group blocking traffic" by looking directly at the
REJECT entries logged; detecting exfiltration by observing an
outbound volume outside the expected pattern; meeting a compliance
requirement (PCI, for example, requires logging network traffic); and
doing cost analysis, revealing exactly who talks to whom inside the
infrastructure.</p>

<h3>8. Limitations and pitfalls</h3>
<p>A CIDR must not overlap between VPCs that will ever connect via
peering or Transit Gateway — discovering that conflict six months
after both are already in production turns a planning decision into a
painful and risky migration. AWS reserves 5 IPs in every subnet
(network address, router, DNS, one reserved for future use, and the
broadcast address), which means a <code>/28</code> subnet nominally
holding 16 addresses actually delivers only 11 usable ones. A subnet
exists in exactly ONE AZ — high availability requires, at minimum, two
subnets in different AZs per layer of the architecture. The default
VPC ships with insecure configuration out of the box, and should be
deleted (or at least never used) in a production account. And, as
already seen in section 5, VPC peering is not transitive — chaining
peerings while expecting automatic transit is a common mistake that
only shows up once someone actually tries to reach the third
endpoint.</p>

<h3>9. Defense in layers</h3>
<p>Defense in depth at the network level stacks six successive
layers, each one assuming the previous one CAN fail: a dedicated VPC
for especially sensitive data (PCI scope, for example); an isolated
subnet for the database, with no route to the internet at all; a NACL
doing broad blocking across the whole subnet; a Security Group
applying fine-grained rules per individual instance; a host firewall
(ufw, nftables) as an extra safety net even within the machine
itself; and finally the application itself with WAF, authentication,
and authorization. No single layer should ever be the only line of
defense.</p>

<h3>10. Real case: the $80k NAT Gateway</h3>
<p>In 2022, a startup publicly reported an $80 thousand bill in a
single month, entirely from NAT Gateway — the machine learning
pipeline was downloading a model from Hugging Face hosted on public
S3, going out through the NAT and back over the internet on an
unnecessarily long path. The fix combined a local cache with a VPC
Endpoint for S3 (possible precisely because the Hugging Face image is
hosted there), and the bill dropped to about $200 a month. The
practical lesson straight from section 4: every gigabyte of egress
through a NAT Gateway costs $0.045 — at scale, that adds up fast
enough to become the biggest line item on the invoice before anyone
notices in time.</p>"""
                ),
                "practical": (
                    "Construa via Terraform (ou console) uma VPC <code>10.10.0.0/16</code> "
                    "com:<br>"
                    "(1) 2 subnets públicas <code>/24</code> em AZs diferentes;<br>"
                    "(2) 2 subnets privadas <code>/24</code> em AZs diferentes;<br>"
                    "(3) IGW + 1 NAT Gateway na pública A (HA simplificado);<br>"
                    "(4) Route tables apropriadas;<br>"
                    "(5) VPC Endpoint Gateway para S3, apontando para route table "
                    "privada.<br>"
                    "(6) Suba uma EC2 em subnet privada. <code>aws s3 cp</code> de algum "
                    "objeto deve funcionar e <em>não</em> aparecer no log do NAT.<br>"
                    "(7) Habilite VPC Flow Logs. Faça uma chamada bloqueada (curl em IP "
                    "fora) e veja o REJECT no log.<br>"
                    "(8) Bônus: planeje IP para 4 ambientes (prod, staging, dev, sandbox) "
                    "em uma org com peering futuro, desenhe em papel."
                ),
                "practical_en": (
                    "Build via Terraform (or the console) a VPC <code>10.10.0.0/16</code> "
                    "with:<br>"
                    "(1) 2 public subnets, <code>/24</code>, in different AZs;<br>"
                    "(2) 2 private subnets, <code>/24</code>, in different AZs;<br>"
                    "(3) IGW + 1 NAT Gateway in public subnet A (simplified HA);<br>"
                    "(4) Appropriate route tables;<br>"
                    "(5) A VPC Endpoint Gateway for S3, pointing at the private "
                    "route table.<br>"
                    "(6) Launch an EC2 instance in the private subnet. <code>aws s3 cp</code> "
                    "against some object should work and <em>should not</em> show up in the "
                    "NAT's log.<br>"
                    "(7) Enable VPC Flow Logs. Make a blocked call (curl to an IP "
                    "outside) and check the REJECT entry in the log.<br>"
                    "(8) Bonus: plan IPs for 4 environments (prod, staging, dev, sandbox) "
                    "in an org with future peering in mind; sketch it on paper."
                ),
            },
            "materials": [
                m("AWS VPC User Guide",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
                  "docs", "",
                  title_en="AWS VPC User Guide",
                  description_en=""),
                m("Azure Virtual Network",
                  "https://learn.microsoft.com/azure/virtual-network/virtual-networks-overview",
                  "docs", "",
                  title_en="Azure Virtual Network",
                  description_en=""),
                m("GCP VPC overview",
                  "https://cloud.google.com/vpc/docs/overview", "docs", "",
                  title_en="GCP VPC overview",
                  description_en=""),
                m("AWS Networking Workshop",
                  "https://catalog.workshops.aws/networking/en-US", "course", "",
                  title_en="AWS Networking Workshop",
                  description_en=""),
                m("CIDR Calculator", "https://cidr.xyz/", "tool", "",
                  title_en="CIDR Calculator",
                  description_en=""),
                m("VPC Endpoints (AWS)",
                  "https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html",
                  "docs", "",
                  title_en="VPC Endpoints (AWS)",
                  description_en=""),
            ],
            "questions": [
                q("Subnet privada NÃO tem:",
                  "Rota para Internet Gateway.",
                  ["Tabela de rota associada à subnet, controlando o destino do pacote.",
                   "Endereço IP atribuído a cada interface de rede dentro da subnet.",
                   "Security Group aplicado à instância que vive dentro da subnet."],
                  "Sem rota para IGW, instâncias não recebem tráfego direto da internet.",
                  statement_en="A private subnet does NOT have:",
                  correct_en="A route to an Internet Gateway.",
                  wrong_en=["A route table associated with the subnet, controlling packet destinations.",
                            "An IP address assigned to each network interface inside the subnet.",
                            "A Security Group applied to the instance living inside the subnet."],
                  explanation_en="Without a route to an IGW, instances don't receive traffic directly from the internet."),
                q("Para outbound de subnet privada:",
                  "Use NAT Gateway.",
                  ["Use o Internet Gateway de forma direta, pulando qualquer intermediário no caminho.",
                   "Use Direct Connect, uma linha dedicada até o datacenter próprio.",
                   "Não é possível ter saída de internet numa subnet privada dessa forma."],
                  "NAT Gateway permite saída sem expor a instância. Caro: considere VPC Endpoint quando o destino é AWS.",
                  statement_en="For outbound from a private subnet:",
                  correct_en="Use a NAT Gateway.",
                  wrong_en=["Use the Internet Gateway directly, skipping any intermediary along the path.",
                            "Use Direct Connect, a dedicated line to your own datacenter.",
                            "Internet egress from a private subnet is not possible that way."],
                  explanation_en="A NAT Gateway allows egress without exposing the instance. Expensive: consider a "
                  "VPC Endpoint when the destination is AWS."),
                q("CIDR /16 em AWS VPC permite quantos hosts aproximadamente?",
                  "65 mil",
                  ["256", "1024", "infinitos"],
                  "/16 = 2^16 = 65.536 endereços. Subdivida em /24 (256 cada) ou /22, conforme necessidade.",
                  statement_en="A /16 CIDR in an AWS VPC allows roughly how many hosts?",
                  correct_en="65 thousand",
                  wrong_en=["256", "1024", "infinite"],
                  explanation_en="/16 = 2^16 = 65,536 addresses. Subdivide into /24 (256 each) or /22 as needed."),
                q("VPC Peering serve para:",
                  "Conectar duas VPCs com IPs distintos.",
                  ["Cobrar valor adicional na fatura mensal de uma conta específica.",
                   "Substituir a resolução de nome feita normalmente pelo DNS interno.",
                   "Conectar container dentro do mesmo host, sem envolver rede alguma."],
                  "Peering é 1:1. Para muitas VPCs, use Transit Gateway (hub-and-spoke).",
                  statement_en="VPC Peering is used to:",
                  correct_en="Connect two VPCs with non-overlapping IPs.",
                  wrong_en=["Add an extra charge on a specific account's monthly bill.",
                            "Replace name resolution normally handled by internal DNS.",
                            "Connect a container on the same host without involving any network."],
                  explanation_en="Peering is 1:1. For many VPCs, use Transit Gateway (hub-and-spoke)."),
                q("Por que múltiplas AZs?",
                  "Resiliência a falhas de datacenter inteiro.",
                  ["Reduz o custo mensal pago pela infraestrutura de rede utilizada.",
                   "Aumenta a latência entre instância dentro da mesma aplicação.",
                   "Não é uma prática recomendada para ambiente de produção real."],
                  "AZ é unidade de falha; deploy multi-AZ é o mínimo para serviços de produção.",
                  statement_en="Why multiple AZs?",
                  correct_en="Resilience to an entire datacenter failing.",
                  wrong_en=["It lowers the monthly cost paid for the network infrastructure in use.",
                            "It increases latency between instances inside the same application.",
                            "It is not a recommended practice for a real production environment."],
                  explanation_en="An AZ is the unit of failure; multi-AZ deploy is the minimum for production services."),
                q("Route table define:",
                  "Para onde pacotes de uma subnet vão.",
                  ["Versão do protocolo TLS aceito pela conexão HTTPS da aplicação.",
                   "Permissão do IAM concedida a um usuário ou role específico.",
                   "Tamanho máximo do pacote (MTU) aceito por uma interface de rede."],
                  "Cada destino (CIDR) tem next-hop (IGW, NAT, peering, gateway endpoint, etc.).",
                  statement_en="A route table defines:",
                  correct_en="Where packets from a subnet go.",
                  wrong_en=["Which TLS protocol version is accepted by the application's HTTPS connection.",
                            "The IAM permission granted to a specific user or role.",
                            "The maximum packet size (MTU) accepted by a network interface."],
                  explanation_en="Each destination (CIDR) has a next-hop (IGW, NAT, peering, gateway endpoint, etc.)."),
                q("Endpoint VPC para S3 reduz:",
                  "Tráfego que sai pela internet, vai pela rede da AWS.",
                  ["Latência para qualquer destino fora da infraestrutura da AWS.",
                   "Necessidade de configurar IAM para acessar o bucket do S3.",
                   "O custo cobrado pelo armazenamento de dado dentro do S3."],
                  "Custos de NAT despencam e exposição também. Use Gateway Endpoint para S3/DynamoDB.",
                  statement_en="A VPC Endpoint for S3 reduces:",
                  correct_en="Traffic that would leave via the internet; it stays on the AWS network.",
                  wrong_en=["Latency to any destination outside AWS infrastructure.",
                            "The need to configure IAM to access the S3 bucket.",
                            "The cost charged for storing data inside S3."],
                  explanation_en="NAT costs drop sharply, and exposure does too. Use a Gateway Endpoint for S3/DynamoDB."),
                q("Internet Gateway é:",
                  "Recurso que permite conectividade bidirecional pública.",
                  ["Um proxy reverso que intermedia a conexão entre cliente e servidor.",
                   "Um firewall que filtra pacote antes dele chegar à instância.",
                   "Um recurso exclusivo para tráfego IPv6, sem suporte a IPv4."],
                  "IGW associado à VPC + rota 0.0.0.0/0 → IGW na route table = subnet pública.",
                  statement_en="An Internet Gateway is:",
                  correct_en="A resource that enables bidirectional public connectivity.",
                  wrong_en=["A reverse proxy that intermediates the connection between client and server.",
                            "A firewall that filters packets before they reach the instance.",
                            "A resource exclusive to IPv6 traffic, with no IPv4 support."],
                  explanation_en="IGW attached to the VPC + route 0.0.0.0/0 → IGW in the route table = public subnet."),
                q("Em VPC, qual recurso é stateful?",
                  "Security Groups.",
                  ["Route Tables, que definem destino, não estado de conexão.",
                   "Subnets, que são só blocos de IP dentro da VPC, sem estado.",
                   "NACLs, que filtram tráfego sem lembrar o estado da conexão."],
                  "SG entende a conexão (stateful). NACL é stateless, precisa configurar inbound E outbound.",
                  statement_en="In a VPC, which resource is stateful?",
                  correct_en="Security Groups.",
                  wrong_en=["Route Tables, which define destinations, not connection state.",
                            "Subnets, which are just IP blocks inside the VPC, with no state.",
                            "NACLs, which filter traffic without remembering connection state."],
                  explanation_en="SGs understand the connection (stateful). NACLs are stateless — you must configure "
                  "inbound AND outbound."),
                q("CIDR sobreposto entre VPCs causa:",
                  "Problema em peering, não é permitido.",
                  ["Backup automático configurado entre as duas VPCs envolvidas.",
                   "Aceleração real do tráfego entre as duas VPCs conectadas.",
                   "Alta disponibilidade extra para a aplicação rodando ali."],
                  "Pacotes não saberiam para qual VPC ir. Planeje CIDRs com IP plan global.",
                  statement_en="Overlapping CIDRs between VPCs cause:",
                  correct_en="A peering problem; it is not allowed.",
                  wrong_en=["Automatic backup configured between the two VPCs involved.",
                            "Real acceleration of traffic between the two connected VPCs.",
                            "Extra high availability for the application running there."],
                  explanation_en="Packets would not know which VPC to go to. Plan CIDRs with a global IP plan."),
            ],
        },
        # =====================================================================
        # 2.5 Security Groups & ACLs
        # =====================================================================
        {
            "title": "Security Groups & ACLs",
            "title_en": "Security Groups & ACLs",
            "summary": "O firewall da nuvem protegendo suas instâncias.",
            "summary_en": "The cloud's firewall protecting your instances.",
            "lesson": {
                "intro": (
                    "Security Groups e NACLs são as duas camadas de filtro de pacotes na AWS, "
                    "e provavelmente os recursos mais mal-entendidos do dia-a-dia. Confundir "
                    "stateful com stateless gera horas perdidas em troubleshooting. Liberar "
                    "<code>0.0.0.0/0:22</code> 'para testar' aparece em quase todo incidente "
                    "público.<br><br>"
                    "Esta aula mostra como cada um funciona, quando usar cada um, padrões "
                    "modernos (referenciar SG por SG-id), bastion vs SSM, e como auditar "
                    "regras de forma escalável."
                ),
                "intro_en": (
                    "Security Groups and NACLs are the two packet-filtering layers in AWS, "
                    "and probably the most misunderstood resources in day-to-day work. Confusing "
                    "stateful with stateless wastes hours of troubleshooting. Opening "
                    "<code>0.0.0.0/0:22</code> 'just to test' shows up in almost every public "
                    "incident.<br><br>"
                    "This lesson shows how each one works, when to use each, modern patterns "
                    "(referencing an SG by SG-id), bastion vs SSM, and how to audit rules "
                    "at scale."
                ),
                "body": (
                """<h3>1. Security Group (SG): stateful, por interface</h3>
<p>Um Security Group é um conjunto de regra Allow associado a uma
interface de rede específica (ENI), com cinco características que
diferenciam completamente sua operação de um firewall tradicional.
Ele é <strong>stateful</strong>: se o inbound na porta 443/tcp é
permitido, a resposta de saída acontece automaticamente, sem precisar
de nenhuma regra outbound correspondente — o SG entende que aquele
tráfego de resposta faz parte da mesma conexão já autorizada. Ele é
<strong>allow-only</strong>: não existe regra de Deny explícita — se
nenhum SG associado permite algo, esse algo simplesmente fica negado
por omissão. O default de inbound nega tudo, enquanto o outbound
permite tudo — e em ambiente sensível, restringir esse outbound
default é uma boa prática subutilizada (seção 5). Cada interface pode
carregar até 5 SGs simultaneamente (limite ajustável). E qualquer regra
nova entra em vigor em segundos, sem nenhum delay de propagação
perceptível.</p>
<div class="mermaid">
flowchart TB
    subgraph SG ["Security Group, stateful"]
        SGIn["Regra de entrada permite porta 443"] --> SGOut["Resposta sai sozinha, sem regra extra"]
    end
    subgraph NACL ["Network ACL, stateless"]
        NIn["Regra de entrada permite porta 443"] --> NOut["Resposta de saída precisa de regra própria"]
    end
</div>


<h3>2. NACL: stateless, por subnet</h3>
<p>A Network ACL filtra na borda da SUBNET inteira, não da interface
individual, e se comporta de forma fundamentalmente diferente do SG.
Ela é <strong>stateless</strong>: cada fluxo precisa de regra explícita
tanto de entrada quanto de saída — esquecer de liberar a faixa de porta
efêmera (1024-65535) no outbound é a causa clássica do sintoma "meu
serviço não responde" mesmo com tudo aparentemente liberado (seção 9).
Ela suporta tanto <strong>Allow quanto Deny</strong>, avaliadas em
ordem numérica até encontrar o primeiro match. O default de uma NACL
gerada automaticamente permite tudo, enquanto uma NACL custom criada do
zero começa negando tudo. E ela se aplica a TODO tráfego entrando ou
saindo da subnet, sem exceção por instância individual. NACL é útil
para bloqueio amplo (banir um IP de atacante de uma subnet inteira de
uma vez), atender exigência de compliance específica sobre porta
bloqueada numa subnet determinada, e como camada extra de defesa em
profundidade — mas não substitui o controle granular por instância, que
é exatamente o papel do Security Group.</p>

<h3>3. Encadeando SGs por referência (chain de SGs)</h3>
<p>Em vez de liberar porta por IP fixo, o padrão mais robusto é liberar
por SG-ID — referenciando outro Security Group diretamente como
origem, não um endereço:</p>
<pre><code># SG do ALB
alb_sg:
  inbound:
    - 443/tcp from 0.0.0.0/0       # internet
    - 80/tcp from 0.0.0.0/0        # redireciona para 443
  outbound:
    - all to app_sg                # fala com app

# SG dos app servers
app_sg:
  inbound:
    - 8000/tcp from alb_sg         # tráfego do ALB
  outbound:
    - 5432/tcp to db_sg            # postgres
    - 443/tcp to 0.0.0.0/0         # APIs externas

# SG do banco
db_sg:
  inbound:
    - 5432/tcp from app_sg         # apenas app fala
  outbound: (nada)</code></pre>
<p>Essa abordagem traz quatro vantagens sobre liberar por IP: a regra
SEGUE a instância automaticamente — quando o auto-scaling adiciona uma
instância nova ao grupo, ela já entra com o acesso correto, sem
reconfigurar nada; a cadeia de SGs se torna literalmente legível como
um diagrama de arquitetura, ALB → app → banco; nenhum IP fica
hard-coded em lugar nenhum; e a auditoria fica trivial, porque "quem
fala com quem" está explícito na própria estrutura de referência entre
SGs.</p>

<h3>4. Bastion vs SSM Session Manager</h3>
<table>
<tr><th>Bastion clássico</th><th>SSM Session Manager (recomendado)</th></tr>
<tr><td>VM exposta com SSH em IP corporativo</td>
<td>Sem porta aberta; agente faz reverse tunnel</td></tr>
<tr><td>Chaves SSH espalhadas</td>
<td>Acesso via IAM (sem chave SSH em produção)</td></tr>
<tr><td>Auditoria via syslog do bastion</td>
<td>Auditoria automática em CloudTrail + S3 (cada comando)</td></tr>
<tr><td>Manutenção (patches, upgrades)</td>
<td>Sem instância para manter</td></tr>
<tr><td>Acesso via internet</td>
<td>Acesso via console ou CLI sem expor nada</td></tr>
</table>
<p>A diferença mais significativa dessa tabela é a linha de superfície
de ataque: um bastion clássico É uma porta SSH exposta na internet,
mesmo que restrita a um IP corporativo — ainda é um alvo. O SSM Session
Manager elimina essa porta inteiramente, usando um agente que faz o
tunnel reverso a partir de dentro da rede, autenticado por IAM em vez
de chave SSH:</p>
<pre><code>aws ssm start-session --target i-0abc123
# ou para port-forwarding (acessar RDS pelo seu laptop):
aws ssm start-session --target i-0abc123 \\
  --document-name AWS-StartPortForwardingSessionToRemoteHost \\
  --parameters host=mydb.cluster.us-east-1.rds.amazonaws.com,portNumber=5432,localPortNumber=5432</code></pre>

<h3>5. Outbound, restringir é boa prática</h3>
<p>O default de um SG é outbound completamente aberto — em ambiente
sensível, vale a pena restringir isso deliberadamente: a aplicação fala
com o banco só pela porta específica e SG específico dele; a
aplicação fala com API da própria AWS via VPC Endpoint (evitando
inclusive o custo de NAT visto na aula anterior); e a aplicação fala
com API externa conhecida apenas na porta 443, idealmente restrita a
domínio específico via proxy de egress. Um outbound restrito elimina
uma classe inteira de ataque: exfiltração de dado e DNS tunneling
dependem justamente de conseguir mandar tráfego para fora sem
restrição nenhuma.</p>

<h3>6. Egress filtering com proxy</h3>
<p>Em ambiente com exigência de compliance mais pesada, o tráfego
HTTPS de saída pode ser forçado a passar por um proxy explícito (Squid,
mitmproxy) que aplica uma whitelist de domínio permitido. Combinado com
um SG outbound que só permite falar com o próprio proxy, o resultado é
uma dupla trava: a aplicação só alcança o proxy, e o proxy só deixa
passar tráfego para domínio explicitamente autorizado.</p>

<h3>7. Anti-patterns recorrentes</h3>
<table>
<tr><td><code>0.0.0.0/0:22</code> em prod</td>
<td>Brute force constante. Sempre aparece em incidente.</td></tr>
<tr><td><code>0.0.0.0/0:3306</code> ou <code>:5432</code> em prod</td>
<td>Banco direto na internet. Ransomware aproveita.</td></tr>
<tr><td>SG 'allow-all' usado em tudo</td>
<td>Vira 'sem firewall' efetivo.</td></tr>
<tr><td>NACL custom com 'allow all' em primeira regra</td>
<td>Inútil; tira camada de defesa.</td></tr>
<tr><td>Liberar 0.0.0.0/0 'temporariamente' e esquecer</td>
<td>Use cron/expiry de tag para alertar regras temporárias.</td></tr>
<tr><td>Criar SG via console manual em vez de Terraform</td>
<td>Drift, sem auditoria, sem revisão.</td></tr>
</table>

<h3>8. Auditoria contínua</h3>
<p>Cinco ferramentas cobrem auditoria contínua de regra de rede em
camadas diferentes: os VPC Flow Logs mostram tanto tráfego permitido
quanto rejeitado de fato; uma AWS Config Rule como
"restricted-ssh" dispara alerta assim que um SG surge com a porta 22
aberta amplamente; o Cloud Custodian pode remediar AUTOMATICAMENTE um
SG com <code>0.0.0.0/0</code> aberto depois de um prazo definido, sem
esperar intervenção humana; o Steampipe permite rodar SQL direto sobre
o estado real da infraestrutura — uma consulta como
<code>select * from aws_vpc_security_group_rule where cidr_ipv4 =
'0.0.0.0/0' and from_port = 22</code> encontra imediatamente toda
exposição desse tipo; e revisar o <code>terraform plan</code> dentro do
próprio PR garante revisão humana antes de qualquer mudança de regra
chegar a ser aplicada de fato.</p>

<h3>9. NACLs efêmeras e o pegadinha do NAT</h3>
<p>Tráfego saindo por um NAT Gateway sai usando uma porta efêmera
alocada dinamicamente, e a resposta volta endereçada exatamente para
essa mesma porta. Se a NACL outbound tem "permit all" mas a inbound só
libera 443, a resposta de uma requisição HTTPS legítima que VOCÊ
mesmo iniciou simplesmente não consegue voltar — porque ela chega numa
porta efêmera, não na 443. A correção é liberar também a faixa
1024-65535 no inbound:</p>
<pre><code># NACL inbound
100  allow 443/tcp  from 0.0.0.0/0   # se subnet pública
110  allow 1024-65535/tcp from 0.0.0.0/0  # respostas de outbound</code></pre>

<h3>10. Caso real: o RDP exposto</h3>
<p>Em 2023, o Shadowserver Project reportou cerca de 3,5 milhões de
servidores Windows com a porta 3389 (RDP) exposta diretamente na
internet, incluindo instâncias rodando em AWS e Azure. Bot automatizado
faz brute-force constante contra qualquer porta RDP visível
publicamente, 24 horas por dia. A alternativa correta segue exatamente
o padrão da seção 4: usar Bastion Host com MFA, log e lockdown
configurados, ou preferencialmente AWS SSM/Azure Bastion, que elimina a
porta exposta por completo; restringir o IP de origem à VPN
corporativa quando um bastion ainda for necessário; e manter Network
Level Authentication (NLA) sempre ativado como camada adicional. O
custo de tirar RDP da internet é de aproximadamente um dia de
configuração — o custo de não tirar é, com frequência crescente,
ransomware.</p>"""
                ),
                "body_en": (
                """<h3>1. Security Group (SG): stateful, per interface</h3>
<p>A Security Group is a set of Allow rules attached to a specific
network interface (ENI), with five characteristics that completely
distinguish its operation from a traditional firewall. It is
<strong>stateful</strong>: if inbound on port 443/tcp is allowed, the
outbound response happens automatically, with no need for any matching
outbound rule — the SG understands that returning traffic is part of
the same already-authorized connection. It is <strong>allow-only</strong>:
there is no explicit Deny rule — if no attached SG allows something,
that something is simply denied by omission. The inbound default
denies everything, while outbound allows everything — and in a
sensitive environment, restricting that outbound default is an
underused good practice (section 5). Each interface can carry up to 5
SGs at once (adjustable limit). And any new rule takes effect within
seconds, with no noticeable propagation delay.</p>
<div class="mermaid">
flowchart TB
    subgraph SG ["Security Group, stateful"]
        SGIn["Regra de entrada permite porta 443"] --> SGOut["Resposta sai sozinha, sem regra extra"]
    end
    subgraph NACL ["Network ACL, stateless"]
        NIn["Regra de entrada permite porta 443"] --> NOut["Resposta de saída precisa de regra própria"]
    end
</div>


<h3>2. NACL: stateless, per subnet</h3>
<p>The Network ACL filters at the edge of the entire SUBNET, not at
the individual interface, and behaves in a fundamentally different way
from the SG. It is <strong>stateless</strong>: every flow needs an
explicit rule for both inbound and outbound — forgetting to open the
ephemeral port range (1024-65535) on outbound is the classic cause of
the "my service isn't responding" symptom even with everything
apparently open (section 9). It supports both <strong>Allow and
Deny</strong>, evaluated in numeric order until the first match is
found. The default of an auto-generated NACL allows everything, while
a custom NACL built from scratch starts by denying everything. And it
applies to ALL traffic entering or leaving the subnet, with no
per-instance exception. NACL is useful for broad blocking (banning an
attacker's IP from an entire subnet at once), meeting a specific
compliance requirement about a blocked port on a given subnet, and as
an extra layer of defense in depth — but it does not replace granular
per-instance control, which is exactly the Security Group's role.</p>

<h3>3. Chaining SGs by reference (SG chain)</h3>
<p>Instead of opening a port by fixed IP, the more robust pattern is
to open it by SG-ID — referencing another Security Group directly as
the source, not an address:</p>
<pre><code># SG do ALB
alb_sg:
  inbound:
    - 443/tcp from 0.0.0.0/0       # internet
    - 80/tcp from 0.0.0.0/0        # redireciona para 443
  outbound:
    - all to app_sg                # fala com app

# SG dos app servers
app_sg:
  inbound:
    - 8000/tcp from alb_sg         # tráfego do ALB
  outbound:
    - 5432/tcp to db_sg            # postgres
    - 443/tcp to 0.0.0.0/0         # APIs externas

# SG do banco
db_sg:
  inbound:
    - 5432/tcp from app_sg         # apenas app fala
  outbound: (nada)</code></pre>
<p>This approach brings four advantages over opening by IP: the rule
automatically FOLLOWS the instance — when auto-scaling adds a new
instance to the group, it already comes in with the correct access, no
reconfiguration needed; the SG chain becomes literally readable as an
architecture diagram, ALB → app → database; no IP is hard-coded
anywhere; and auditing becomes trivial, because "who talks to whom" is
explicit in the reference structure between SGs itself.</p>

<h3>4. Bastion vs SSM Session Manager</h3>
<table>
<tr><th>Classic bastion</th><th>SSM Session Manager (recommended)</th></tr>
<tr><td>VM exposed with SSH on a corporate IP</td>
<td>No open port; agent does a reverse tunnel</td></tr>
<tr><td>SSH keys scattered around</td>
<td>Access via IAM (no SSH key in production)</td></tr>
<tr><td>Auditing via the bastion's syslog</td>
<td>Automatic auditing in CloudTrail + S3 (every command)</td></tr>
<tr><td>Maintenance (patches, upgrades)</td>
<td>No instance to maintain</td></tr>
<tr><td>Access over the internet</td>
<td>Access via console or CLI with nothing exposed</td></tr>
</table>
<p>The most significant difference in this table is the attack-surface
row: a classic bastion IS an SSH port exposed on the internet, even if
restricted to a corporate IP — it's still a target. SSM Session
Manager eliminates that port entirely, using an agent that makes the
reverse tunnel from inside the network, authenticated via IAM instead
of an SSH key:</p>
<pre><code>aws ssm start-session --target i-0abc123
# ou para port-forwarding (acessar RDS pelo seu laptop):
aws ssm start-session --target i-0abc123 \\
  --document-name AWS-StartPortForwardingSessionToRemoteHost \\
  --parameters host=mydb.cluster.us-east-1.rds.amazonaws.com,portNumber=5432,localPortNumber=5432</code></pre>

<h3>5. Outbound, restricting is a good practice</h3>
<p>The default for an SG is fully open outbound — in a sensitive
environment, it's worth restricting this deliberately: the application
talks to the database only on its specific port and specific SG; the
application talks to AWS's own API via VPC Endpoint (also avoiding the
NAT cost seen in the previous lesson); and the application talks to a
known external API only on port 443, ideally restricted to a specific
domain via an egress proxy. A restricted outbound eliminates an entire
class of attack: data exfiltration and DNS tunneling both depend
precisely on being able to send traffic out with no restriction at
all.</p>

<h3>6. Egress filtering with a proxy</h3>
<p>In an environment with heavier compliance requirements, outbound
HTTPS traffic can be forced through an explicit proxy (Squid,
mitmproxy) that applies an allowed-domain whitelist. Combined with an
outbound SG that only allows talking to the proxy itself, the result is
a double lock: the application only reaches the proxy, and the proxy
only lets through traffic to an explicitly authorized domain.</p>

<h3>7. Recurring anti-patterns</h3>
<table>
<tr><td><code>0.0.0.0/0:22</code> in prod</td>
<td>Constant brute force. Always shows up in an incident.</td></tr>
<tr><td><code>0.0.0.0/0:3306</code> or <code>:5432</code> in prod</td>
<td>Database directly on the internet. Ransomware takes advantage.</td></tr>
<tr><td>'allow-all' SG used everywhere</td>
<td>Becomes an effective 'no firewall'.</td></tr>
<tr><td>Custom NACL with 'allow all' as the first rule</td>
<td>Useless; removes a layer of defense.</td></tr>
<tr><td>Opening 0.0.0.0/0 'temporarily' and forgetting</td>
<td>Use a cron/tag-expiry to flag temporary rules.</td></tr>
<tr><td>Creating an SG via manual console instead of Terraform</td>
<td>Drift, no audit trail, no review.</td></tr>
</table>

<h3>8. Continuous auditing</h3>
<p>Five tools cover continuous network-rule auditing at different
layers: VPC Flow Logs show both traffic that was actually allowed and
traffic that was rejected; an AWS Config Rule like "restricted-ssh"
fires an alert as soon as an SG shows up with port 22 broadly open;
Cloud Custodian can AUTOMATICALLY remediate an SG with
<code>0.0.0.0/0</code> open after a defined grace period, without
waiting for human intervention; Steampipe lets you run SQL directly
against the real state of the infrastructure — a query like
<code>select * from aws_vpc_security_group_rule where cidr_ipv4 =
'0.0.0.0/0' and from_port = 22</code> immediately finds every exposure
of that kind; and reviewing the <code>terraform plan</code> right
inside the PR guarantees human review before any rule change actually
gets applied.</p>

<h3>9. Ephemeral NACLs and the NAT gotcha</h3>
<p>Traffic leaving through a NAT Gateway goes out using a dynamically
allocated ephemeral port, and the response comes back addressed to
that exact same port. If the outbound NACL has "permit all" but
inbound only allows 443, the response to a legitimate HTTPS request
that YOU yourself initiated simply can't come back — because it
arrives on an ephemeral port, not on 443. The fix is to also open the
1024-65535 range on inbound:</p>
<pre><code># NACL inbound
100  allow 443/tcp  from 0.0.0.0/0   # se subnet pública
110  allow 1024-65535/tcp from 0.0.0.0/0  # respostas de outbound</code></pre>

<h3>10. Real case: exposed RDP</h3>
<p>In 2023, the Shadowserver Project reported around 3.5 million
Windows servers with port 3389 (RDP) exposed directly on the internet,
including instances running on AWS and Azure. Automated bots run
constant brute force against any publicly visible RDP port, 24 hours
a day. The correct alternative follows exactly the pattern from
section 4: use a Bastion Host with MFA, logging and lockdown
configured, or preferably AWS SSM/Azure Bastion, which eliminates the
exposed port entirely; restrict the source IP to the corporate VPN
when a bastion is still needed; and keep Network Level Authentication
(NLA) always enabled as an extra layer. The cost of taking RDP off the
internet is roughly one day of configuration — the cost of not doing
so is, with increasing frequency, ransomware.</p>"""
                ),
                "practical": (
                    "(1) Crie um SG <code>web</code> permitindo 443 de 0.0.0.0/0 e 22 "
                    "<em>apenas</em> do seu IP fixo (não 0.0.0.0/0).<br>"
                    "(2) Crie um SG <code>db</code> permitindo 5432 apenas de SG "
                    "<code>web</code> (referência por SG-id, não por IP).<br>"
                    "(3) Suba uma EC2 com SG <code>web</code> e um RDS com SG "
                    "<code>db</code>. De fora, tente <code>nc -zv &lt;rds-endpoint&gt; "
                    "5432</code>, deve falhar. Da EC2, deve funcionar.<br>"
                    "(4) Habilite VPC Flow Logs e veja o REJECT na primeira tentativa.<br>"
                    "(5) Configure SSM Agent na EC2 e acesse via "
                    "<code>aws ssm start-session</code>, sem nenhuma porta aberta para "
                    "internet.<br>"
                    "(6) Bônus: escreva a mesma config em Terraform e aplique. Veja como "
                    "fica versionável."
                ),
                "practical_en": (
                    "(1) Create a <code>web</code> SG allowing 443 from 0.0.0.0/0 and 22 "
                    "<em>only</em> from your fixed IP (not 0.0.0.0/0).<br>"
                    "(2) Create a <code>db</code> SG allowing 5432 only from the "
                    "<code>web</code> SG (reference by SG-id, not by IP).<br>"
                    "(3) Spin up an EC2 with the <code>web</code> SG and an RDS with the "
                    "<code>db</code> SG. From outside, try <code>nc -zv &lt;rds-endpoint&gt; "
                    "5432</code>, it should fail. From the EC2, it should work.<br>"
                    "(4) Enable VPC Flow Logs and watch the REJECT on the first attempt.<br>"
                    "(5) Configure the SSM Agent on the EC2 and connect via "
                    "<code>aws ssm start-session</code>, with no port open to the "
                    "internet.<br>"
                    "(6) Bonus: write the same config in Terraform and apply it. See how "
                    "it becomes versionable."
                ),
            },
            "materials": [
                m("AWS Security Groups",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html",
                  "docs", "",
                  title_en="AWS Security Groups",
                  description_en=""),
                m("AWS NACLs",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html",
                  "docs", "",
                  title_en="AWS NACLs",
                  description_en=""),
                m("Azure NSG",
                  "https://learn.microsoft.com/azure/virtual-network/network-security-groups-overview",
                  "docs", "",
                  title_en="Azure NSG",
                  description_en=""),
                m("GCP Firewall Rules",
                  "https://cloud.google.com/firewall/docs/firewalls", "docs", "",
                  title_en="GCP Firewall Rules",
                  description_en=""),
                m("Cloudflare: stateful vs stateless firewall",
                  "https://www.cloudflare.com/learning/network-layer/what-is-a-stateful-firewall/",
                  "article", "",
                  title_en="Cloudflare: stateful vs stateless firewall",
                  description_en=""),
                m("AWS SSM Session Manager",
                  "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html",
                  "docs", "Substitui bastion+SSH em muitos casos.",
                  title_en="AWS SSM Session Manager",
                  description_en="Replaces bastion+SSH in many cases."),
            ],
            "questions": [
                q("Security Group em AWS é:",
                  "Stateful, resposta automática.",
                  ["Stateless, precisa de regra separada para tráfego de resposta.",
                   "Aplicado por host físico inteiro, não por interface de rede individual.",
                   "Restrito só a tráfego IPv6, sem suporte a IPv4 disponível."],
                  "Stateful = inbound libera o retorno do outbound automaticamente. NACL é o oposto.",
                  statement_en="A Security Group in AWS is:",
                  correct_en="Stateful, automatic response.",
                  wrong_en=["Stateless, needs a separate rule for the response traffic.",
                            "Applied to the entire physical host, not to an individual network interface.",
                            "Restricted only to IPv6 traffic, with no available IPv4 support."],
                  explanation_en="Stateful = inbound automatically allows the outbound return. NACL is the opposite."),
                q("NACL em AWS é:",
                  "Stateless, precisa regras de saída e entrada.",
                  ["Restrito só ao protocolo IPv4, sem cobertura para tráfego IPv6.",
                   "Aplicado à instância inteira, não à interface de rede especificamente.",
                   "Stateful, libera resposta automaticamente sem regra adicional."],
                  "Esquecer regra outbound de portas efêmeras é fonte clássica de 'meu serviço não responde'.",
                  statement_en="An NACL in AWS is:",
                  correct_en="Stateless, needs both outbound and inbound rules.",
                  wrong_en=["Restricted only to the IPv4 protocol, with no coverage for IPv6 traffic.",
                            "Applied to the whole instance, not specifically to the network interface.",
                            "Stateful, allows the response automatically with no extra rule."],
                  explanation_en="Forgetting the outbound rule for ephemeral ports is the classic source of 'my service isn't responding'."),
                q("Por padrão, SG inbound:",
                  "Bloqueia tudo.",
                  ["Libera acesso só pela porta usada pelo protocolo SSH.",
                   "Permite qualquer tráfego de entrada, sem restrição alguma configurada previamente.",
                   "Aceita conexão nas portas 80 e 443 por padrão de fábrica."],
                  "Default-deny, você precisa abrir explicitamente o que quer.",
                  statement_en="By default, SG inbound:",
                  correct_en="Blocks everything.",
                  wrong_en=["Allows access only through the port used by the SSH protocol.",
                            "Allows any inbound traffic, with no restriction configured beforehand.",
                            "Accepts connections on ports 80 and 443 by factory default."],
                  explanation_en="Default-deny, you need to explicitly open what you want."),
                q("Em SG, posso permitir tráfego vindo de outro SG?",
                  "Sim, referenciando o SG-id no source.",
                  ["Só é possível autorizando pelo lado do IAM, não pelo SG.",
                   "Não, cada Security Group só enxerga tráfego por IP fixo.",
                   "Restrito só a tráfego IPv6, sem aceitar referência de outro SG."],
                  "Encadeamento por SG é a melhor prática para evitar IP hardcoded.",
                  statement_en="In an SG, can I allow traffic coming from another SG?",
                  correct_en="Yes, by referencing the SG-id as the source.",
                  wrong_en=["It's only possible by authorizing on the IAM side, not on the SG.",
                            "No, each Security Group only recognizes traffic by fixed IP.",
                            "Restricted only to IPv6 traffic, with no support for referencing another SG."],
                  explanation_en="Chaining by SG is the best practice to avoid hard-coded IPs."),
                q("NACL avalia regras:",
                  "Em ordem numérica até encontrar match.",
                  ["Considera só a última regra cadastrada, ignorando as anteriores.",
                   "De forma aleatória, sem ordem definida entre as regras existentes.",
                   "Baseado no timestamp de criação de cada regra individual."],
                  "Por isso convenciona-se números (100, 200, 300...) e regra final 32766/deny all.",
                  statement_en="An NACL evaluates rules:",
                  correct_en="In numeric order until it finds a match.",
                  wrong_en=["It only considers the last rule registered, ignoring the previous ones.",
                            "Randomly, with no defined order among the existing rules.",
                            "Based on the creation timestamp of each individual rule."],
                  explanation_en="That's why numbering conventions (100, 200, 300...) plus a final deny-all rule at 32766 are used."),
                q("Para HTTPS, qual porta liberar?",
                  "443 TCP.",
                  ["8443 TCP, uma porta alternativa às vezes usada por proxy.",
                   "443 UDP, usado por QUIC/HTTP-3, não pelo HTTPS clássico.",
                   "80 UDP, uma combinação que não corresponde a um uso comum na prática."],
                  "443 TCP é o padrão; HTTP/3 usa 443 UDP, mas só libere se a app for HTTP/3.",
                  statement_en="For HTTPS, which port should be opened?",
                  correct_en="443 TCP.",
                  wrong_en=["8443 TCP, an alternate port sometimes used by a proxy.",
                            "443 UDP, used by QUIC/HTTP-3, not by classic HTTPS.",
                            "80 UDP, a combination that doesn't match a common use case in practice."],
                  explanation_en="443 TCP is the standard; HTTP/3 uses 443 UDP, but only open it if the app actually speaks HTTP/3."),
                q("SG aplica-se a:",
                  "Interfaces de rede (ENIs).",
                  ["Subnet inteira, aplicando a mesma regra a cada IP dentro dela.",
                   "Só ao protocolo IPv6, sem cobertura para tráfego IPv4.",
                   "Só a função Lambda, sem aplicar a outro tipo de recurso."],
                  "ENI pode ter até 5 SGs (limite ajustável). Lambda em VPC também usa SG da ENI.",
                  statement_en="An SG applies to:",
                  correct_en="Network interfaces (ENIs).",
                  wrong_en=["The entire subnet, applying the same rule to every IP inside it.",
                            "Only the IPv6 protocol, with no coverage for IPv4 traffic.",
                            "Only the Lambda function, with no application to any other resource type."],
                  explanation_en="An ENI can have up to 5 SGs (adjustable limit). Lambda inside a VPC also uses the ENI's SG."),
                q("Boas práticas com SG:",
                  "Granularidade alta, sem 0.0.0.0/0 desnecessário.",
                  ["Abrir 0.0.0.0/0 de entrada em qualquer porta disponível do servidor.",
                   "Deixar de atualizar a regra por meses, mesmo com mudança de escopo.",
                   "Usar o mesmo Security Group compartilhado pela infraestrutura inteira."],
                  "Granular = mais regras, mas auditável e principle of least access.",
                  statement_en="Good practices with SGs:",
                  correct_en="High granularity, no unnecessary 0.0.0.0/0.",
                  wrong_en=["Opening 0.0.0.0/0 inbound on any available port of the server.",
                            "Leaving the rule unchanged for months, even after a change in scope.",
                            "Using the same shared Security Group across the entire infrastructure."],
                  explanation_en="Granular means more rules, but auditable and aligned with the principle of least access."),
                q("Permitir 0.0.0.0/0 em SSH é:",
                  "Risco crítico de força bruta.",
                  ["Uma boa prática recomendada para ambiente de produção real.",
                   "Bloqueia completamente o serviço sshd assim que aplicado.",
                   "Necessário para o protocolo SSH funcionar de alguma forma."],
                  "Use bastion, VPN ou SSM Session Manager. SSH público em produção = manchete esperando acontecer.",
                  statement_en="Allowing 0.0.0.0/0 on SSH is:",
                  correct_en="A critical brute-force risk.",
                  wrong_en=["A recommended good practice for a real production environment.",
                            "Completely blocks the sshd service as soon as it's applied.",
                            "Necessary for the SSH protocol to work in any way at all."],
                  explanation_en="Use a bastion, VPN, or SSM Session Manager. Public SSH in production is a headline waiting to happen."),
                q("Como auditar uso de SG?",
                  "VPC Flow Logs e CloudTrail.",
                  ["Não é possível auditar esse tipo de mudança de forma alguma disponível hoje.",
                   "Rodar o comando top dentro do próprio servidor monitorado.",
                   "Consultar só o histórico de resolução de nome feito via DNS."],
                  "Flow Logs mostra tráfego; CloudTrail mostra mudanças nas regras.",
                  statement_en="How do you audit SG usage?",
                  correct_en="VPC Flow Logs and CloudTrail.",
                  wrong_en=["It's not possible to audit this kind of change with anything available today.",
                            "Run the top command inside the monitored server itself.",
                            "Only check the name-resolution history recorded via DNS."],
                  explanation_en="Flow Logs show traffic; CloudTrail shows changes to the rules."),
            ],
        },
        # =====================================================================
        # 2.6 Object Storage (S3)
        # =====================================================================
        {
            "title": "Object Storage (S3)",
            "title_en": "Object Storage (S3)",
            "summary": "Armazenamento de arquivos e permissões de acesso público/privado.",
            "summary_en": "File storage and public/private access permissions.",
            "lesson": {
                "intro": (
                    "S3 (e seus primos Azure Blob Storage e Google Cloud Storage) sustenta "
                    "a internet moderna: hospeda imagens de containers, modelos de ML, vídeos "
                    "do YouTube, sites estáticos, backups, logs, data lakes. É o serviço cloud "
                    "mais usado e o mais frequentemente mal-configurado.<br><br>"
                    "Vazamentos de S3 público estão na manchete há mais de uma década, "
                    "Verizon, Accenture, Twilio, Booz Allen Hamilton, FedEx, e milhares de "
                    "casos menores. Esta aula é uma imersão em modelo de dados, controle de "
                    "acesso, padrões seguros de upload, lifecycle, encryption e como NÃO "
                    "ser a próxima manchete."
                ),
                "intro_en": (
                    "S3 (and its cousins Azure Blob Storage and Google Cloud Storage) powers "
                    "the modern internet: it hosts container images, ML models, YouTube "
                    "videos, static sites, backups, logs, data lakes. It's the most-used "
                    "cloud service and the most frequently misconfigured one.<br><br>"
                    "Public S3 leaks have made headlines for over a decade — Verizon, "
                    "Accenture, Twilio, Booz Allen Hamilton, FedEx, and thousands of smaller "
                    "cases. This lesson is a deep dive into the data model, access control, "
                    "secure upload patterns, lifecycle, encryption, and how NOT to be the "
                    "next headline."
                ),
                "body": (
                """<h3>1. Modelo de dados: object storage não é filesystem</h3>
<p>S3 quebra a intuição de quem espera um sistema de arquivo
tradicional. Não existem diretórios de verdade, apenas prefixos —
<code>fotos/2025/janeiro/foo.jpg</code> é uma chave única, uma string
inteira, não uma hierarquia real de pastas navegáveis. Não existe
operação de append nem rename genuíno — sobrescrever significa fazer o
upload completo do objeto de novo, não editar em lugar. Cada objeto
combina arquivo, metadado, tag e ACL num único pacote. A latência de
listagem cresce com o número de prefixos, o que empurra design de data
lake a usar particionamento estilo Hive
(<code>year=2025/month=04/...</code>) para manter as listagens
rápidas. E a consistência é read-after-write forte, inclusive logo após
um delete — uma garantia que nem todo object storage oferece. Para
quem precisa mesmo assim de comportamento de filesystem, existem
Mountpoint for S3 e s3fs-fuse, mas vale saber de antemão que operação
de <em>list</em> e <em>rename</em> continuam caras nesse modelo, não
importa a camada de abstração por cima.</p>
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "PUT bucket, key" --> API["API do object storage"]
    API --> Bucket["Bucket"]
    Bucket --> Obj["Objeto: key + valor + metadado"]
</div>


<h3>2. Controle de acesso, em ordem cronológica</h3>
<p>O S3 acumulou camada sobre camada de controle de acesso ao longo
dos anos, na ordem em que foram introduzidas: primeiro vieram as
<strong>ACLs</strong> (legado) — grant por dono de bucket ou objeto,
hoje desabilitadas por default, e que não deveriam ser usadas em
projeto novo. Depois vieram as <strong>Bucket Policies</strong>
(resource-based) — um JSON anexado diretamente ao bucket, capaz de
permitir acesso cross-account ou até anônimo quando necessário. Em
paralelo existem as <strong>IAM Policies</strong> (identity-based) —
permissão atrelada à identidade que faz a chamada, combinada com a
bucket policy na avaliação final. E por cima de tudo isso está o
<strong>Block Public Access</strong> (BPA) — um override de "segurança
primeiro" que bloqueia QUALQUER acesso público mesmo que uma policy
mais permissiva diga o contrário. A regra de ouro segue direto dessa
hierarquia: ativar Block Public Access na CONTA inteira por padrão, e
liberar bucket público apenas quando o bucket for explicitamente
destinado a CDN ou site estático (seção 8).</p>

<h3>3. Padrões de policy de bucket</h3>
<pre><code># Forçar HTTPS em todo o bucket
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyInsecureConnections",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::meu-bucket",
      "arn:aws:s3:::meu-bucket/*"
    ],
    "Condition": {
      "Bool": {"aws:SecureTransport": "false"}
    }
  }]
}

# Cross-account leitura (delegação)
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::OUTRA_CONTA:role/data-reader"},
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::meu-bucket",
      "arn:aws:s3:::meu-bucket/dataset/*"
    ]
  }]
}</code></pre>

<h3>4. Upload seguro: presigned URL</h3>
<p>O anti-pattern comum é o cliente fazer upload via backend, que
tunela os bytes até o S3 — isso transforma o backend num gargalo, paga
custo de banda em dobro (recebendo do cliente e reenviando ao S3), e
ainda mantém credencial de S3 no próprio backend desnecessariamente. O
padrão correto é a <strong>presigned URL</strong>: o backend gera uma
URL assinada com TTL curto (5 minutos) e parâmetro restrito, e o
cliente faz upload DIRETO para o S3, sem passar pelo backend em
nenhum momento:</p>
<pre><code>import boto3
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

url = s3.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': 'meu-bucket',
        'Key': f'uploads/{user_id}/{file_id}.jpg',
        'ContentType': 'image/jpeg',
        'ContentLength': 5_000_000,           # max 5 MB
        'Metadata': {'user-id': str(user_id)},
    },
    ExpiresIn=300,                            # 5 minutos
)
# Retorna ao cliente; ele faz PUT direto.</code></pre>
<p>Para segurança adicional, um presigned POST vai além, permitindo
restrição baseada em policy — limite de tamanho, whitelist de
content-type — que o cliente não consegue burlar mesmo manipulando a
requisição diretamente.</p>

<h3>5. Encryption: SSE-S3, SSE-KMS, SSE-C, client-side</h3>
<table>
<tr><th>Modo</th><th>Chave gerenciada por</th><th>Auditoria</th><th>Caso de uso</th></tr>
<tr><td>SSE-S3</td><td>AWS</td><td>baixa</td>
<td>Default 'só ative algo'</td></tr>
<tr><td>SSE-KMS (AWS-managed)</td><td>AWS via KMS</td><td>média</td>
<td>Encryption padrão</td></tr>
<tr><td>SSE-KMS (CMK)</td><td>Você (Customer Managed Key)</td>
<td>alta, log de cada uso da key</td>
<td>Compliance (PCI/HIPAA), revogação granular</td></tr>
<tr><td>SSE-C</td><td>Você manda chave a cada request</td>
<td>nenhuma na AWS</td><td>Casos especiais</td></tr>
<tr><td>Client-side</td><td>Você criptografa antes</td>
<td>nenhuma</td><td>Zero-trust no provedor</td></tr>
</table>
<p>Em 2023, a AWS passou a habilitar SSE-S3 por padrão em todo bucket
novo, fechando o caso mais básico de "esqueceram de ativar encryption".
Mesmo assim, para caso sensível de verdade, ainda vale especificar
explicitamente SSE-KMS com CMK — a diferença de auditoria entre "chave
gerenciada pela AWS" e "chave gerenciada por você, com log de cada uso"
é significativa em qualquer investigação de incidente.</p>

<h3>6. Versionamento + Object Lock = anti-ransomware</h3>
<p>Cenário concreto: um atacante consegue credencial com permissão de
delete no S3 e apaga tudo. É o fim? Não, se quatro proteções já
estiverem em vigor ANTES do incidente. O <strong>versionamento</strong>
faz cada PUT criar uma versão nova, e um delete gerar apenas um "delete
marker" recuperável, não uma remoção real. O <strong>MFA Delete</strong>
exige MFA do root especificamente para apagar uma versão, uma barreira
extra além da permissão IAM comum. O <strong>Object Lock em modo
Compliance</strong> impede até o root de apagar antes do prazo de
retenção configurado — um modelo WORM (Write Once, Read Many) genuíno.
A <strong>Cross-Region Replication</strong> mantém uma cópia em região
separada, com bucket policy independente. E a <strong>Cross-Account
Replication</strong> mantém uma cópia numa conta AWS totalmente
separada — um atacante que comprometa a conta principal não alcança
essa cópia. Combinar as quatro é o que realmente sustenta defesa contra
ransomware sério, não apenas uma delas isolada.</p>

<h3>7. Lifecycle: economizando 90% em logs antigos</h3>
<table>
<tr><th>Classe</th><th>$/GB-mês</th><th>Latência</th><th>Caso</th></tr>
<tr><td>Standard</td><td>~0.023</td><td>ms</td><td>dados quentes</td></tr>
<tr><td>Standard-IA</td><td>~0.0125</td><td>ms</td><td>infrequente,
&gt;30d</td></tr>
<tr><td>Intelligent-Tiering</td><td>auto</td><td>ms</td><td>quando não
sabe o padrão de acesso</td></tr>
<tr><td>Glacier Instant</td><td>~0.004</td><td>ms</td>
<td>arquivos &gt;90d</td></tr>
<tr><td>Glacier Flexible</td><td>~0.0036</td><td>min-horas</td>
<td>backup &gt;90d</td></tr>
<tr><td>Glacier Deep Archive</td><td>~0.00099</td><td>12h</td>
<td>compliance &gt;180d</td></tr>
</table>
<p>Uma regra de lifecycle típica para log move o dado automaticamente
entre classes conforme envelhece, sem intervenção manual:</p>
<pre><code>{
  "Rules": [{
    "ID": "logs-tiering",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30,  "StorageClass": "STANDARD_IA"},
      {"Days": 90,  "StorageClass": "GLACIER_IR"},
      {"Days": 180, "StorageClass": "DEEP_ARCHIVE"}
    ],
    "Expiration": {"Days": 2555}        
  }]
}</code></pre>
<p>Vale calcular antes o custo de retrieval — o Glacier cobra
especificamente para TIRAR dado de lá, o que pode anular boa parte da
economia se o padrão de acesso real for mais frequente do que o
esperado no planejamento.</p>

<h3>8. Site estático + CloudFront: arquitetura segura</h3>
<p>Ao hospedar uma SPA (React, Vue) em S3 atrás de CloudFront, o bucket
NÃO precisa — e não deveria — ser público. O Origin Access Control
(OAC) resolve isso mantendo o bucket privado e permitindo leitura só a
partir da distribuição CloudFront específica:</p>
<pre><code># Bucket policy permite só CloudFront
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "cloudfront.amazonaws.com"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::site-bucket/*",
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::123:distribution/EXXX"
      }
    }
  }]
}</code></pre>
<p>Com essa policy, o bucket fica completamente privado e apenas a
distribuição específica referenciada no <code>SourceArn</code> consegue
ler seu conteúdo — o CloudFront então serve tudo com TLS, cache e
cabeçalho de segurança por cima.</p>

<h3>9. Logging e detecção</h3>
<p>Quatro mecanismos cobrem detecção em diferentes granularidades. Os
<strong>S3 Access Logs</strong> registram cada requisição, entregues em
outro bucket, úteis mas com delivery atrasado em horas, não em tempo
real. Os <strong>CloudTrail Data Events</strong> registram cada
GetObject ou PutObject diretamente no CloudTrail — caro em alta escala,
por isso vale habilitar seletivamente só em bucket realmente sensível.
O <strong>Macie</strong> escaneia buckets em busca de PII — CPF,
cartão, e-mail — classificando o risco automaticamente sem precisar de
regra manual escrita à mão. E o <strong>GuardDuty S3 Protection</strong>
faz detecção comportamental: exfiltração, bucket público criado sem
autorização, ou padrão de listagem anômalo.</p>

<h3>10. Caso real: Capital One revisitado</h3>
<p>O que vazou no incidente descrito na aula anterior foi obtido via
comando simples <code>s3 ls</code> seguido de <code>s3 sync</code>,
usando a credencial temporária capturada via SSRF — 700 buckets, 100
milhões de registros. Se algumas das proteções desta aula já
estivessem em vigor, o desfecho teria sido diferente: uma bucket policy
restringindo acesso a um VPC Endpoint específico teria negado a
listagem vinda de fora daquele contexto; o Macie alertando volume de
download anômalo teria sinalizado o incidente em andamento; o GuardDuty
detectando exfiltração de dado teria disparado o mesmo alerta por outro
ângulo; e uma VPC sem rota direta para S3 público, forçando tudo via
endpoint, teria limitado o próprio caminho de saída do dado. Com
qualquer uma dessas camadas ativa, o ataque teria sido detectado em
horas — não nos meses que de fato levou até vir à tona.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Bucket público sem necessidade real</strong>: a exposição
mais comum e mais evitável de todas.</li>
<li><strong>Credencial hard-coded em código mobile ou frontend</strong>:
qualquer um que descompile o app extrai a chave imediatamente.</li>
<li><strong>Sem versionamento</strong>: perde a proteção descrita na
seção 6 contra delete acidental ou malicioso.</li>
<li><strong>Sem encryption</strong>: mesmo com SSE-S3 hoje default,
ainda existe bucket antigo criado antes dessa mudança sem nenhuma
camada de encryption.</li>
<li><strong>Nome de bucket sequencial e adivinhável</strong>
(<code>backup-prod-1</code>, <code>backup-prod-2</code>): facilita
enumeração automatizada por atacante fazendo scan em massa.</li>
<li><strong>Sem lifecycle</strong>: log de cinco anos atrás continua
pagando o preço de Standard, sem nenhum motivo técnico.</li>
<li><strong>Cross-account sem trilha de auditoria</strong>: torna
impossível responder depois "quem acessou o quê e quando".</li>
<li><strong>Object ACL em vez de bucket policy</strong>: usa o
mecanismo legado da seção 2 quando a alternativa moderna já resolve
melhor o mesmo problema.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Data model: object storage is not a filesystem</h3>
<p>S3 breaks the intuition of anyone expecting a traditional
filesystem. There are no real directories, only prefixes —
<code>fotos/2025/janeiro/foo.jpg</code> is a single key, one whole
string, not a real navigable folder hierarchy. There's no append
operation and no genuine rename — overwriting means uploading the
entire object again, not editing in place. Each object bundles file,
metadata, tags, and ACL into a single package. Listing latency grows
with the number of prefixes, which pushes data-lake design toward
Hive-style partitioning (<code>year=2025/month=04/...</code>) to keep
listings fast. And consistency is strongly read-after-write, including
right after a delete — a guarantee not every object storage offers.
For anyone who still needs filesystem-like behavior, there's
Mountpoint for S3 and s3fs-fuse, but it's worth knowing upfront that
<em>list</em> and <em>rename</em> operations stay expensive in this
model, no matter the abstraction layer on top.</p>
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "PUT bucket, key" --> API["API do object storage"]
    API --> Bucket["Bucket"]
    Bucket --> Obj["Objeto: key + valor + metadado"]
</div>


<h3>2. Access control, in chronological order</h3>
<p>S3 has accumulated layer upon layer of access control over the
years, in the order they were introduced: first came <strong>ACLs</strong>
(legacy) — grants by bucket or object owner, disabled by default
today, and which shouldn't be used in a new project. Then came
<strong>Bucket Policies</strong> (resource-based) — a JSON document
attached directly to the bucket, capable of allowing cross-account or
even anonymous access when needed. In parallel there are <strong>IAM
Policies</strong> (identity-based) — permission tied to the identity
making the call, combined with the bucket policy in the final
evaluation. And on top of all of that sits <strong>Block Public
Access</strong> (BPA) — a "security first" override that blocks ANY
public access even if a more permissive policy says otherwise. The
golden rule follows directly from this hierarchy: enable Block Public
Access at the ACCOUNT level by default, and only allow a public bucket
when it's explicitly meant for a CDN or static site (section 8).</p>

<h3>3. Bucket policy patterns</h3>
<pre><code># Forçar HTTPS em todo o bucket
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyInsecureConnections",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::meu-bucket",
      "arn:aws:s3:::meu-bucket/*"
    ],
    "Condition": {
      "Bool": {"aws:SecureTransport": "false"}
    }
  }]
}

# Cross-account leitura (delegação)
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::OUTRA_CONTA:role/data-reader"},
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::meu-bucket",
      "arn:aws:s3:::meu-bucket/dataset/*"
    ]
  }]
}</code></pre>

<h3>4. Secure upload: presigned URL</h3>
<p>The common anti-pattern is having the client upload via the
backend, which tunnels the bytes through to S3 — this turns the
backend into a bottleneck, pays bandwidth cost twice (receiving from
the client and re-sending to S3), and still unnecessarily keeps an S3
credential on the backend itself. The correct pattern is the
<strong>presigned URL</strong>: the backend generates a signed URL with
a short TTL (5 minutes) and a restricted parameter, and the client
uploads DIRECTLY to S3, never passing through the backend at all:</p>
<pre><code>import boto3
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

url = s3.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': 'meu-bucket',
        'Key': f'uploads/{user_id}/{file_id}.jpg',
        'ContentType': 'image/jpeg',
        'ContentLength': 5_000_000,           # max 5 MB
        'Metadata': {'user-id': str(user_id)},
    },
    ExpiresIn=300,                            # 5 minutos
)
# Retorna ao cliente; ele faz PUT direto.</code></pre>
<p>For extra security, a presigned POST goes further, allowing
policy-based restrictions — size limit, content-type whitelist — that
the client can't bypass even by tampering with the request directly.</p>

<h3>5. Encryption: SSE-S3, SSE-KMS, SSE-C, client-side</h3>
<table>
<tr><th>Mode</th><th>Key managed by</th><th>Auditing</th><th>Use case</th></tr>
<tr><td>SSE-S3</td><td>AWS</td><td>low</td>
<td>Default 'just turn something on'</td></tr>
<tr><td>SSE-KMS (AWS-managed)</td><td>AWS via KMS</td><td>medium</td>
<td>Standard encryption</td></tr>
<tr><td>SSE-KMS (CMK)</td><td>You (Customer Managed Key)</td>
<td>high, logs every use of the key</td>
<td>Compliance (PCI/HIPAA), granular revocation</td></tr>
<tr><td>SSE-C</td><td>You send the key with every request</td>
<td>none on AWS</td><td>Special cases</td></tr>
<tr><td>Client-side</td><td>You encrypt before uploading</td>
<td>none</td><td>Zero-trust in the provider</td></tr>
</table>
<p>In 2023, AWS started enabling SSE-S3 by default on every new
bucket, closing the most basic case of "forgot to turn on encryption."
Even so, for genuinely sensitive cases, it's still worth explicitly
specifying SSE-KMS with a CMK — the auditing difference between "key
managed by AWS" and "key managed by you, with a log of every use" is
significant in any incident investigation.</p>

<h3>6. Versioning + Object Lock = anti-ransomware</h3>
<p>Concrete scenario: an attacker gets hold of a credential with
delete permission on S3 and wipes everything. Is that the end? No, if
four protections are already in place BEFORE the incident.
<strong>Versioning</strong> makes every PUT create a new version, and a
delete only generates a recoverable "delete marker," not a real
removal. <strong>MFA Delete</strong> requires root MFA specifically to
delete a version, an extra barrier beyond regular IAM permission.
<strong>Object Lock in Compliance mode</strong> prevents even root from
deleting before the configured retention period — a genuine WORM
(Write Once, Read Many) model. <strong>Cross-Region Replication</strong>
keeps a copy in a separate region, with an independent bucket policy.
And <strong>Cross-Account Replication</strong> keeps a copy in a
completely separate AWS account — an attacker who compromises the main
account doesn't reach that copy. Combining all four is what actually
sustains defense against serious ransomware, not just one of them in
isolation.</p>

<h3>7. Lifecycle: saving 90% on old logs</h3>
<table>
<tr><th>Class</th><th>$/GB-month</th><th>Latency</th><th>Case</th></tr>
<tr><td>Standard</td><td>~0.023</td><td>ms</td><td>hot data</td></tr>
<tr><td>Standard-IA</td><td>~0.0125</td><td>ms</td><td>infrequent,
&gt;30d</td></tr>
<tr><td>Intelligent-Tiering</td><td>auto</td><td>ms</td><td>when you
don't know the access pattern</td></tr>
<tr><td>Glacier Instant</td><td>~0.004</td><td>ms</td>
<td>files &gt;90d</td></tr>
<tr><td>Glacier Flexible</td><td>~0.0036</td><td>min-hours</td>
<td>backup &gt;90d</td></tr>
<tr><td>Glacier Deep Archive</td><td>~0.00099</td><td>12h</td>
<td>compliance &gt;180d</td></tr>
</table>
<p>A typical lifecycle rule for logs automatically moves data between
classes as it ages, with no manual intervention:</p>
<pre><code>{
  "Rules": [{
    "ID": "logs-tiering",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30,  "StorageClass": "STANDARD_IA"},
      {"Days": 90,  "StorageClass": "GLACIER_IR"},
      {"Days": 180, "StorageClass": "DEEP_ARCHIVE"}
    ],
    "Expiration": {"Days": 2555}
  }]
}</code></pre>
<p>It's worth calculating retrieval cost beforehand — Glacier
specifically charges to TAKE data out of it, which can wipe out much
of the savings if the real access pattern turns out more frequent than
originally planned.</p>

<h3>8. Static site + CloudFront: secure architecture</h3>
<p>When hosting an SPA (React, Vue) on S3 behind CloudFront, the
bucket does NOT need — and shouldn't — be public. Origin Access
Control (OAC) solves this by keeping the bucket private and allowing
reads only from the specific CloudFront distribution:</p>
<pre><code># Bucket policy permite só CloudFront
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "cloudfront.amazonaws.com"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::site-bucket/*",
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::123:distribution/EXXX"
      }
    }
  }]
}</code></pre>
<p>With this policy, the bucket stays completely private and only the
specific distribution referenced in <code>SourceArn</code> can read
its content — CloudFront then serves everything with TLS, caching,
and security headers on top.</p>

<h3>9. Logging and detection</h3>
<p>Four mechanisms cover detection at different granularities.
<strong>S3 Access Logs</strong> record every request, delivered to
another bucket, useful but with delivery delayed by hours, not
real-time. <strong>CloudTrail Data Events</strong> record every
GetObject or PutObject directly in CloudTrail — expensive at high
scale, so it's worth enabling selectively only on genuinely sensitive
buckets. <strong>Macie</strong> scans buckets looking for PII — SSNs,
card numbers, emails — classifying the risk automatically with no
hand-written rule needed. And <strong>GuardDuty S3 Protection</strong>
does behavioral detection: exfiltration, an unauthorized public bucket
being created, or an anomalous listing pattern.</p>

<h3>10. Real case: Capital One revisited</h3>
<p>What leaked in the incident described in the previous lesson was
obtained via a simple <code>s3 ls</code> followed by <code>s3
sync</code>, using a temporary credential captured through SSRF — 700
buckets, 100 million records. If some of the protections from this
lesson had already been in place, the outcome would have been
different: a bucket policy restricting access to a specific VPC
Endpoint would have denied the listing coming from outside that
context; Macie alerting on an anomalous download volume would have
flagged the incident in progress; GuardDuty detecting data
exfiltration would have triggered the same alert from another angle;
and a VPC with no direct route to public S3, forcing everything
through an endpoint, would have limited the data's own exit path. With
any one of these layers active, the attack would have been detected
within hours — not the months it actually took to come to light.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Public bucket with no real need</strong>: the most common
and most avoidable exposure of all.</li>
<li><strong>Hard-coded credential in mobile or frontend code</strong>:
anyone who decompiles the app extracts the key immediately.</li>
<li><strong>No versioning</strong>: loses the protection described in
section 6 against accidental or malicious delete.</li>
<li><strong>No encryption</strong>: even with SSE-S3 now default,
there's still an old bucket created before that change with no
encryption layer at all.</li>
<li><strong>Sequential, guessable bucket name</strong>
(<code>backup-prod-1</code>, <code>backup-prod-2</code>): makes
automated enumeration easy for an attacker running a mass scan.</li>
<li><strong>No lifecycle</strong>: a five-year-old log keeps paying
Standard pricing, for no technical reason.</li>
<li><strong>Cross-account with no audit trail</strong>: makes it
impossible to later answer "who accessed what and when."</li>
<li><strong>Object ACL instead of bucket policy</strong>: uses the
legacy mechanism from section 2 when the modern alternative already
solves the same problem better.</li>
</ul>"""
                ),
                "practical": (
                    "(1) Crie um bucket privado, ative Block Public Access (todas as 4 "
                    "flags), encryption SSE-KMS com CMK próprio e versionamento.<br>"
                    "(2) Configure lifecycle: Standard → IA aos 30d, Glacier Instant aos "
                    "90d, Deep Archive aos 365d, expiração aos 7 anos.<br>"
                    "(3) Em uma app, gere um <em>presigned URL PUT</em> com 5 min de TTL e "
                    "<code>Content-Length</code> máximo de 5 MB. Faça o upload via "
                    "<code>curl -T arquivo.jpg URL</code>.<br>"
                    "(4) Apague o objeto. Depois recupere a versão anterior via "
                    "<code>aws s3api list-object-versions</code> + "
                    "<code>copy-object</code>.<br>"
                    "(5) Crie bucket policy negando todo acesso sem "
                    "<code>aws:SecureTransport: true</code>. Teste com curl http (deve "
                    "falhar) e https (deve funcionar).<br>"
                    "(6) Bônus: configure replicação cross-region para outro bucket em "
                    "região diferente."
                ),
                "practical_en": (
                    "(1) Create a private bucket, enable Block Public Access (all 4 "
                    "flags), SSE-KMS encryption with your own CMK, and versioning.<br>"
                    "(2) Configure lifecycle: Standard → IA at 30d, Glacier Instant at "
                    "90d, Deep Archive at 365d, expiration at 7 years.<br>"
                    "(3) In an app, generate a <em>presigned PUT URL</em> with a 5-minute "
                    "TTL and a maximum <code>Content-Length</code> of 5 MB. Upload via "
                    "<code>curl -T arquivo.jpg URL</code>.<br>"
                    "(4) Delete the object. Then recover the previous version via "
                    "<code>aws s3api list-object-versions</code> + "
                    "<code>copy-object</code>.<br>"
                    "(5) Create a bucket policy denying all access without "
                    "<code>aws:SecureTransport: true</code>. Test with curl over http "
                    "(should fail) and https (should work).<br>"
                    "(6) Bonus: configure cross-region replication to another bucket in "
                    "a different region."
                ),
            },
            "materials": [
                m("AWS S3 User Guide",
                  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
                  "docs", "",
                  title_en="AWS S3 User Guide",
                  description_en=""),
                m("Azure Blob Storage",
                  "https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview",
                  "docs", "",
                  title_en="Azure Blob Storage",
                  description_en=""),
                m("GCS docs", "https://cloud.google.com/storage/docs", "docs", "",
                  title_en="GCS docs",
                  description_en=""),
                m("AWS S3 Block Public Access",
                  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html",
                  "docs", "",
                  title_en="AWS S3 Block Public Access",
                  description_en=""),
                m("MinIO (S3 compat)",
                  "https://min.io/docs/minio/linux/index.html", "docs", "",
                  title_en="MinIO (S3 compatible)",
                  description_en=""),
                m("AWS Macie (descobre PII)",
                  "https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html",
                  "docs", "",
                  title_en="AWS Macie (discovers PII)",
                  description_en=""),
            ],
            "questions": [
                q("Bucket público sem necessidade leva a:",
                  "Vazamento de dados.",
                  ["Performance maior de leitura, já que qualquer um pode acessar direto.",
                   "Backup automático feito pelo próprio provedor sem custo adicional.",
                   "Auto-scaling de capacidade de armazenamento conforme demanda cresce."],
                  "Maior parte dos vazamentos cloud nas últimas duas décadas começou em S3 público.",
                  statement_en="An unnecessarily public bucket leads to:",
                  correct_en="Data leakage.",
                  wrong_en=["Higher read performance, since anyone can access it directly.",
                            "Automatic backup done by the provider itself at no extra cost.",
                            "Auto-scaling of storage capacity as demand grows."],
                  explanation_en="Most cloud leaks over the last two decades started with a public S3 bucket."),
                q("Presigned URL serve para:",
                  "Conceder acesso temporário a um objeto sem expor credenciais.",
                  ["Substitui completamente a necessidade de configurar IAM no bucket.",
                   "Renomear arquivo em lote dentro de um bucket já existente.",
                   "Acelerar o upload de arquivo grande usando conexão paralela."],
                  "TTL curto reduz risco. Limite método e tamanho para minimizar abuso.",
                  statement_en="A presigned URL is used to:",
                  correct_en="Grant temporary access to an object without exposing credentials.",
                  wrong_en=["Completely replace the need to ever configure any IAM policy or bucket policy on the bucket at all.",
                            "Batch-rename files inside an already existing bucket.",
                            "Speed up uploading a large file using a parallel connection."],
                  explanation_en="A short TTL reduces risk. Restrict method and size to minimize abuse."),
                q("Versionamento em S3 ajuda em:",
                  "Recuperação após exclusão acidental ou ransomware.",
                  ["Backup financeiro exigido por auditoria contábil da empresa.",
                   "Aumento real do número de IOPS disponível para o bucket.",
                   "Compressão automática aplicada a cada objeto armazenado."],
                  "Combine com MFA Delete e Object Lock para defesa em camadas.",
                  statement_en="Versioning in S3 helps with:",
                  correct_en="Recovery after accidental deletion or ransomware.",
                  wrong_en=["Financial backup required by the company's accounting audit.",
                            "A real increase in the number of IOPS available for the bucket.",
                            "Automatic compression applied to every stored object."],
                  explanation_en="Combine it with MFA Delete and Object Lock for layered defense."),
                q("SSE-KMS criptografa:",
                  "Objetos em repouso usando chaves do KMS.",
                  ["Só o nome do arquivo, sem tocar no conteúdo real do objeto.",
                   "Só a tag associada ao objeto, sem cifrar o conteúdo dele.",
                   "O tráfego em trânsito entre cliente e servidor, via TLS."],
                  "Trânsito é coberto por TLS (HTTPS). KMS adiciona granularidade, você pode "
                  "controlar quem usa cada chave.",
                  statement_en="SSE-KMS encrypts:",
                  correct_en="Objects at rest using KMS keys.",
                  wrong_en=["Only the file name, without touching the object's actual content.",
                            "Only the tag associated with the object, without ciphering its content.",
                            "Traffic in transit between client and server, via TLS."],
                  explanation_en="Transit is covered by TLS (HTTPS). KMS adds granularity, letting you "
                  "control who uses each key."),
                q("'Block Public Access' na conta:",
                  "Garante que nenhum bucket fique exposto por engano.",
                  ["Aumenta o custo mensal cobrado pelo armazenamento no S3.",
                   "Apaga objeto já existente dentro de qualquer bucket da conta.",
                   "Bloqueia a criação de política nova dentro do IAM da conta."],
                  "Quatro flags; ative as quatro a menos que tenha caso justificável de bucket público.",
                  statement_en="'Block Public Access' at the account level:",
                  correct_en="Ensures no bucket ends up exposed by mistake.",
                  wrong_en=["Increases the monthly cost charged for S3 storage.",
                            "Deletes an object that already exists inside any bucket in the account.",
                            "Blocks the creation of a new policy inside the account's IAM."],
                  explanation_en="Four flags; enable all four unless you have a justified case for a public bucket."),
                q("Lifecycle rule pode:",
                  "Mover objetos a Glacier após N dias.",
                  ["Habilita o protocolo HTTPS para as requisições feitas ao bucket.",
                   "Renomeia o bucket inteiro sem precisar recriar o conteúdo.",
                   "Substitui a política de IAM aplicada ao bucket inteiro."],
                  "Reduz custo drasticamente para dados frios. Cuidado com custo de retrieval em Glacier.",
                  statement_en="A lifecycle rule can:",
                  correct_en="Move objects to Glacier after N days.",
                  wrong_en=["Enable the HTTPS protocol for requests made to the bucket.",
                            "Rename the entire bucket without needing to recreate the content.",
                            "Replace the IAM policy applied to the whole bucket."],
                  explanation_en="It drastically cuts costs for cold data. Watch out for Glacier retrieval costs."),
                q("Para hospedar site estático em S3:",
                  "Habilite static website hosting + use CloudFront na frente.",
                  ["Use Route53 isoladamente, sem qualquer outro serviço envolvido no caminho.",
                   "Use Lambda como servidor web, processando cada requisição HTTP recebida.",
                   "Use EC2 dedicada, mantendo o servidor ligado continuamente de forma manual."],
                  "CloudFront + Origin Access Identity permite manter o bucket privado.",
                  statement_en="To host a static site on S3:",
                  correct_en="Enable static website hosting + put CloudFront in front.",
                  wrong_en=["Use Route53 by itself, with no other service involved along the way.",
                            "Use Lambda as a web server, processing every incoming HTTP request.",
                            "Use a dedicated EC2, keeping the server running continuously by hand."],
                  explanation_en="CloudFront + Origin Access Identity lets you keep the bucket private."),
                q("Logs de acesso ao bucket vão para:",
                  "Outro bucket configurado como destino.",
                  ["O CloudWatch sozinho, sem exigir bucket adicional para isso.",
                   "O console da AWS, mostrado direto na tela, sem persistir em lugar algum.",
                   "Um destino que não existe, já que o S3 não gera esse log sozinho."],
                  "Bucket de logs deve ser separado e com policy restritiva. Considere também CloudTrail data events.",
                  statement_en="Access logs for the bucket go to:",
                  correct_en="Another bucket configured as the destination.",
                  wrong_en=["CloudWatch alone, with no additional bucket required for it.",
                            "The AWS console, shown directly on screen, with nothing persisted anywhere.",
                            "A destination that doesn't exist, since S3 doesn't generate this log on its own."],
                  explanation_en="The log bucket should be separate with a restrictive policy. Also consider CloudTrail data events."),
                q("Como evitar deleção acidental?",
                  "Object Lock + versionamento + MFA Delete.",
                  ["Só a policy do IAM aplicada à conta, sem qualquer outra camada configurada.",
                   "Um backup guardado localmente, fora da infraestrutura da AWS.",
                   "Não criar arquivo novo, mantendo o bucket permanentemente vazio."],
                  "Object Lock em modo Compliance impede até root de apagar antes do TTL.",
                  statement_en="How do you prevent accidental deletion?",
                  correct_en="Object Lock + versioning + MFA Delete.",
                  wrong_en=["Only the IAM policy applied to the account, with no other layer configured.",
                            "A backup kept locally, outside of the AWS infrastructure.",
                            "Never creating a new file, keeping the bucket permanently empty."],
                  explanation_en="Object Lock in Compliance mode prevents even root from deleting before the retention period."),
                q("S3 tem garantia de durabilidade nominal de:",
                  "11 noves (99.999999999%).",
                  ["3 noves (99.9%), padrão comum em serviço menos crítico.",
                   "5 noves (99.999%), acima do S3 Standard em disponibilidade.",
                   "Sem garantia formal de durabilidade documentada pelo provedor."],
                  "Calculado replicando objetos cross-AZ. Disponibilidade é menor (4 noves no Standard).",
                  statement_en="S3's nominal durability guarantee is:",
                  correct_en="11 nines (99.999999999%).",
                  wrong_en=["3 nines (99.9%), a common standard for a less critical service.",
                            "5 nines (99.999%), above S3 Standard's actual availability figure.",
                            "No formal durability guarantee documented by the provider at all."],
                  explanation_en="Calculated by replicating objects cross-AZ. Availability is lower (4 nines on Standard)."),
            ],
        },
        # =====================================================================
        # 2.7 Criptografia em Repouso e Trânsito
        # =====================================================================
        {
            "title": "Criptografia em Repouso e Trânsito",
            "title_en": "Encryption at Rest and in Transit",
            "summary": "Proteção de dados com chaves KMS e TLS/SSL.",
            "summary_en": "Protecting data with KMS keys and TLS/SSL.",
            "lesson": {
                "intro": (
                    "Criptografia não é mágica e não substitui controle de acesso, mas não "
                    "usá-la é negligência clara em qualquer auditoria moderna. Felizmente, "
                    "em cloud, a maior parte vem de fábrica: TLS é default em endpoints, "
                    "KMS gerencia chaves para você, e habilitar encryption at rest é um "
                    "checkbox.<br><br>"
                    "Esta aula cobre: o modelo de threat (do que cripto protege e do que "
                    "não), simétrica vs assimétrica, gestão de chaves com KMS, TLS bem "
                    "feito, hashing para senhas, post-quantum no horizonte, e os bugs caros "
                    "que pegam quem confia no default."
                ),
                "intro_en": (
                    "Encryption is not magic and does not replace access control, but not "
                    "using it is clear negligence in any modern audit. Fortunately, "
                    "in the cloud, most of it comes out of the box: TLS is the default on "
                    "endpoints, KMS manages keys for you, and enabling encryption at rest is a "
                    "checkbox.<br><br>"
                    "This lesson covers: the threat model (what encryption protects against and "
                    "what it doesn't), symmetric vs asymmetric, key management with KMS, TLS done "
                    "well, password hashing, post-quantum on the horizon, and the costly bugs "
                    "that catch those who trust the default."
                ),
                "body": (
                """<h3>1. Modelo de ameaça: do que cripto protege</h3>
<p>Antes de qualquer detalhe técnico, vale separar exatamente o que
está sendo protegido em cada cenário. <strong>Em repouso</strong>
significa proteger contra alguém que ganha acesso direto ao disco, ao
snapshot ou ao backup — um provedor de nuvem comprometido, um snapshot
roubado, um disco descartado sem wipe antes do descarte.
<strong>Em trânsito</strong> significa proteger contra alguém
interceptando o tráfego pelo caminho — um ataque man-in-the-middle, um
ISP malicioso, um Wi-Fi público — e é exatamente esse cenário que o TLS
resolve. <strong>Em uso</strong> é o mais difícil dos três: dado
sendo processado ainda dentro da RAM, num momento em que criptografia
convencional simplesmente NÃO protege nada — só Confidential Computing
(Nitro Enclaves, AMD SEV, Intel SGX) endereça esse caso específico.
Vale igualmente entender o que criptografia NÃO faz: não substitui
IAM ou RBAC — se o atacante já está autenticado como usuário válido, ele
lê o dado em claro do mesmo jeito que qualquer usuário legítimo leria;
não protege contra SQL injection nem bug de aplicação; não protege
metadado (timestamp, tamanho de arquivo, padrão de acesso continuam
visíveis mesmo com o conteúdo cifrado); e sem gestão de chave correta,
vira apenas caro e inútil ao mesmo tempo.</p>
<div class="mermaid">
flowchart LR
    subgraph Transito ["Em trânsito"]
        A["Cliente"] -- "TLS" --> B["Servidor"]
    end
    subgraph Repouso ["Em repouso"]
        C["Dado gravado em disco"] --> D["Criptografado com chave do KMS"]
    end
</div>


<h3>2. Simétrica vs assimétrica</h3>
<table>
<tr><th></th><th>Simétrica (AES, ChaCha20)</th>
<th>Assimétrica (RSA, ECC, Ed25519)</th></tr>
<tr><td>Chave</td><td>uma só</td><td>par público + privado</td></tr>
<tr><td>Velocidade</td><td>rápida (~GB/s)</td><td>lenta (~MB/s)</td></tr>
<tr><td>Tamanho de chave</td><td>128/256 bits</td>
<td>2048-4096 bits (RSA), 256 bits (ECC)</td></tr>
<tr><td>Caso de uso</td><td>cifrar dados em volume</td>
<td>troca de chave, assinatura</td></tr>
</table>
<p>O TLS na prática combina os dois de propósito: o handshake
assimétrico (RSA/ECDHE) serve exclusivamente para estabelecer, de
forma segura, uma chave SIMÉTRICA de sessão — que então é a que
realmente cifra o volume de tráfego, aproveitando a velocidade da
simétrica onde importa e a segurança da assimétrica onde é
necessária.</p>

<h3>3. Algoritmos modernos vs depreciados</h3>
<table>
<tr><th>Categoria</th><th>Use</th><th>Evite</th></tr>
<tr><td>Cifra simétrica</td><td>AES-256-GCM, ChaCha20-Poly1305</td>
<td>DES, 3DES, RC4, AES-CBC sem MAC</td></tr>
<tr><td>Hash</td><td>SHA-256, SHA-3, BLAKE2/3</td>
<td>MD5, SHA-1</td></tr>
<tr><td>KDF (senha)</td><td>Argon2id, scrypt, bcrypt</td>
<td>MD5/SHA1 puro, PBKDF2 com baixo custo</td></tr>
<tr><td>Assimétrica chave</td><td>Ed25519, X25519, ECDSA P-256, RSA-3072+</td>
<td>RSA-1024, DSA</td></tr>
<tr><td>TLS</td><td>TLS 1.3 (preferível), 1.2 OK</td>
<td>TLS 1.0/1.1, SSLv3, SSLv2</td></tr>
</table>

<h3>4. KMS, gestão de chaves como serviço</h3>
<p>O KMS resolve o problema crítico de onde efetivamente guardar a
chave — em vez de num arquivo no disco da própria aplicação, ela fica
dentro de um HSM (Hardware Security Module) gerenciado, um chip
dedicado certificado FIPS 140-2 Level 2 ou 3, de onde a chave NUNCA
sai em texto claro. A aplicação interage com isso via API de
encrypt/decrypt — envia o texto puro, recebe o cifrado, sem nunca
manusear a chave diretamente. Cada uso dessa chave fica registrado no
CloudTrail para auditoria completa. A rotação acontece automaticamente
(anual, em CMK gerenciada). E deletar a chave torna o dado protegido
por ela inacessível de propósito — com uma janela de espera de 7 a 30
dias para reverter uma deleção acidental antes que se torne
permanente. O KMS também permite configuração cross-account: um bucket
na conta A criptografado por uma chave gerenciada na conta B, uma
separação de poder deliberada onde comprometer uma conta não dá acesso
automático à chave da outra.</p>

<h3>5. Envelope encryption, escala</h3>
<p>Chamar o KMS diretamente para cada bloco de um terabyte de dado
seria absurdamente ineficiente — o padrão correto é a envelope
encryption, em quatro passos. Primeiro, a aplicação pede uma
<strong>data key</strong> ao KMS: ele gera uma chave AES-256 aleatória,
cifra essa mesma chave com a CMK, e devolve as DUAS versões — a
plaintext e a cifrada. Segundo, a aplicação usa a versão plaintext
dessa data key para cifrar o dado real localmente, com a velocidade
normal de uma cifra simétrica. Terceiro, a aplicação armazena junto
apenas <code>{ciphertext_data, encrypted_data_key}</code> — a versão
plaintext da data key é descartada imediatamente após o uso, nunca
persistida. Para decifrar depois, o processo se inverte: pede ao KMS
para decifrar a <code>encrypted_data_key</code>, recebe a versão
plaintext de volta, e usa ela para decifrar o dado real. O resultado é
que a chave MESTRE nunca sai do HSM em nenhum momento, enquanto a data
key específica de cada dado fica armazenada junto dele — ganhando
performance de cifra local sem abrir mão da segurança centralizada da
chave mestre:</p>
<pre><code>import boto3, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

kms = boto3.client('kms')

# Gerar data key
resp = kms.generate_data_key(KeyId='alias/my-cmk', KeySpec='AES_256')
plaintext_key = resp['Plaintext']
encrypted_key = resp['CiphertextBlob']    # armazenar com o dado

# Cifrar com AES-GCM (autenticada)
aes = AESGCM(plaintext_key)
nonce = os.urandom(12)
ciphertext = aes.encrypt(nonce, b'dados sensiveis', associated_data=b'tenant-x')

# Para decifrar:
plaintext_key = kms.decrypt(CiphertextBlob=encrypted_key)['Plaintext']
data = AESGCM(plaintext_key).decrypt(nonce, ciphertext, b'tenant-x')</code></pre>

<h3>6. TLS 1.3, o melhor jeito de fazer</h3>
<p>O TLS 1.3 resolveu quatro problemas estruturais das versões
anteriores: o handshake caiu para 1 round-trip (contra 2 no TLS 1.2),
com 0-RTT disponível em sessão retomada, reduzindo latência percebida
na conexão inicial; forward secrecy passou a ser OBRIGATÓRIA, com
apenas ECDHE permitido — mesmo que a chave privada do servidor vaze no
futuro, tráfego passado capturado continua indecifrável; cipher suite
legada (RC4, MD5, SHA1) foi removida completamente do protocolo, sem
opção de fallback; e a renegociação, que era historicamente um vetor
de ataque conhecido, foi eliminada de vez. Uma configuração mínima
"modern" (recomendação da Mozilla) fica assim:</p>
<pre><code>ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;</code></pre>
<p>Auditar a configuração final no SSL Labs, mirando nota A+, confirma
que nenhum detalhe ficou esquecido nessa combinação.</p>

<h3>7. mTLS, autenticação mútua</h3>
<p>Um TLS comum só verifica o SERVIDOR, via certificado — o cliente
segue anônimo do ponto de vista criptográfico. O mTLS inverte parte
disso: o servidor TAMBÉM verifica o cliente, criando autenticação nos
dois sentidos. O caso de uso típico é comunicação serviço-a-serviço
dentro de um mesh, onde cada serviço carrega um certificado próprio
emitido por uma CA interna. No Kubernetes, um service mesh (Istio,
Linkerd) automatiza isso inteiramente: cada Pod recebe certificado via
SPIFFE, com rotação a cada 24 horas e validação automática — o
resultado é autenticação criptográfica genuína entre serviços internos,
sem precisar mudar uma linha de código da aplicação em si.</p>

<h3>8. Hashing de senhas, não é encryption</h3>
<p>Hash é unidirecional por definição — dado o resultado, não existe
caminho de volta até a senha original. Mas SHA-256 puro não serve para
senha: um atacante com GPU tenta bilhões de combinação por segundo
contra um hash simples demais. A alternativa correta é uma KDF de
propósito específico, desenhada para ser DELIBERADAMENTE lenta e cara
de paralelizar: o Argon2id venceu a Password Hashing Competition de
2015 e é memory-hard, tornando paralelização em GPU cara mesmo com
hardware dedicado, com parâmetro ajustável de custo de memória,
iteração e paralelismo; o bcrypt continua uma opção clássica aceitável
com cost factor acima de 12; e o scrypt oferece a mesma propriedade
memory-hard do Argon2:</p>
<pre><code>from argon2 import PasswordHasher
ph = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)
hashed = ph.hash('senha-do-usuario')
# salva 'hashed' no banco
ph.verify(hashed, 'senha-do-usuario')</code></pre>
<p>Adicionar salt continua essencial (Argon2 e bcrypt já fazem isso
automaticamente) — sem salt, um atacante resolve o hash inteiro de uma
vez com uma rainbow table pré-computada, em vez de precisar atacar
senha por senha individualmente.</p>

<h3>9. Post-quantum: o que vem aí</h3>
<p>Um computador quântico com qubit suficiente vai quebrar RSA e ECC
via o algoritmo de Shor — a estimativa atual fica entre 10 e 20 anos
para isso se tornar prático. O problema real, porém, é anterior a essa
data: dado criptografado HOJE e capturado por um atacante pode ser
decifrado no futuro assim que essa capacidade existir — o ataque
chamado "harvest now, decrypt later" já está acontecendo neste
momento, mesmo sem o computador quântico capaz de completar a
decifração ainda existir. O NIST publicou em 2024 os primeiros padrões
post-quantum oficiais: ML-KEM (Kyber, para troca de chave) e ML-DSA
(Dilithium, para assinatura). Cloudflare, Google e AWS já oferecem TLS
híbrido opcional, combinando o algoritmo clássico com o post-quantum ao
mesmo tempo — vale considerar isso desde já para qualquer dado cujo
valor de sigilo se estenda além de dez anos no futuro.</p>

<h3>10. Caso real: ROCA, chaves quebradas em massa</h3>
<p>Em 2017, pesquisadores descobriram que uma biblioteca da Infineon
— usada em smart card e módulo TPM amplamente distribuído — gerava
chave RSA-2048 com uma fraqueza matemática específica, permitindo
fatoração da chave com um custo estimado de cerca de US$ 38 mil em
processamento de nuvem alugado. O resultado prático foi a necessidade
de rotacionar chave de governo (incluindo a Estônia inteira), de
corporação, e de milhões de smart cards individuais ao redor do mundo.
As lições diretas: o tamanho nominal da chave (2048 bits) não basta
sozinho — a IMPLEMENTAÇÃO que gera a chave importa tanto quanto o
tamanho declarado; usar biblioteca já amplamente auditada (OpenSSL,
libsodium, BoringSSL) reduz drasticamente esse risco específico de
geração falha; mecanismo de rotação de chave precisa existir desde o
primeiro dia, não ser adicionado depois de um incidente; e um HSM com
firmware atualizável se torna uma vantagem real quando uma falha desse
tipo é descoberta anos depois do deploy original.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Senha em SHA-256 sem salt nem KDF</strong>: exatamente o
erro que a seção 8 existe para corrigir.</li>
<li><strong>Chave estática hard-coded no código</strong>: qualquer um
com acesso ao repositório extrai a chave imediatamente.</li>
<li><strong>TLS com certificado auto-assinado em produção</strong>:
elimina a garantia de identidade que o próprio TLS existe para
prover.</li>
<li><strong>Versão de OpenSSL desatualizada</strong>: mantém CVE
antiga conhecida ativa por escolha, não por acidente.</li>
<li><strong>HSTS sem <code>includeSubDomains</code> e sem
<code>preload</code></strong>: deixa subdomínio ou primeira visita fora
da proteção completa.</li>
<li><strong>Cifra simétrica sem autenticação</strong> (AES-CBC sem
MAC): permite adulteração do ciphertext sem detecção.</li>
<li><strong>IV ou nonce reutilizado</strong>: quebra a garantia de
segurança de praticamente qualquer cifra moderna que dependa dele ser
único.</li>
<li><strong>Encryption at rest sem encryption em trânsito</strong>:
protege o dado parado mas deixa o mesmo dado exposto exatamente no
momento em que trafega pela rede.</li>
<li><strong>"Encriptamos os dados" mas a chave fica no mesmo
disco</strong>: anula completamente o propósito da criptografia — quem
rouba o disco rouba a chave junto.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Threat model: what encryption protects against</h3>
<p>Before any technical detail, it's worth separating exactly what is
being protected in each scenario. <strong>At rest</strong> means
protecting against someone who gains direct access to the disk, the
snapshot, or the backup — a compromised cloud provider, a stolen
snapshot, a disk discarded without a wipe before disposal.
<strong>In transit</strong> means protecting against someone
intercepting traffic along the way — a man-in-the-middle attack, a
malicious ISP, a public Wi-Fi network — and that is exactly the
scenario TLS solves. <strong>In use</strong> is the hardest of the
three: data being processed while still inside RAM, a moment in which
conventional encryption simply does NOT protect anything — only
Confidential Computing (Nitro Enclaves, AMD SEV, Intel SGX) addresses
that specific case. It's equally worth understanding what encryption
does NOT do: it does not replace IAM or RBAC — if the attacker is
already authenticated as a valid user, they read the data in the
clear the same way any legitimate user would; it does not protect
against SQL injection or application bugs; it does not protect
metadata (timestamp, file size, access pattern remain visible even
with the content encrypted); and without correct key management, it
becomes merely expensive and useless at the same time.</p>
<div class="mermaid">
flowchart LR
    subgraph Transito ["Em trânsito"]
        A["Cliente"] -- "TLS" --> B["Servidor"]
    end
    subgraph Repouso ["Em repouso"]
        C["Dado gravado em disco"] --> D["Criptografado com chave do KMS"]
    end
</div>


<h3>2. Symmetric vs asymmetric</h3>
<table>
<tr><th></th><th>Symmetric (AES, ChaCha20)</th>
<th>Asymmetric (RSA, ECC, Ed25519)</th></tr>
<tr><td>Key</td><td>a single one</td><td>public + private pair</td></tr>
<tr><td>Speed</td><td>fast (~GB/s)</td><td>slow (~MB/s)</td></tr>
<tr><td>Key size</td><td>128/256 bits</td>
<td>2048-4096 bits (RSA), 256 bits (ECC)</td></tr>
<tr><td>Use case</td><td>encrypting bulk data</td>
<td>key exchange, signing</td></tr>
</table>
<p>TLS in practice combines both on purpose: the asymmetric handshake
(RSA/ECDHE) serves exclusively to securely establish a SYMMETRIC
session key — which is what actually encrypts the bulk of the
traffic, taking advantage of symmetric speed where it matters and
asymmetric security where it's needed.</p>

<h3>3. Modern vs deprecated algorithms</h3>
<table>
<tr><th>Category</th><th>Use</th><th>Avoid</th></tr>
<tr><td>Symmetric cipher</td><td>AES-256-GCM, ChaCha20-Poly1305</td>
<td>DES, 3DES, RC4, AES-CBC without MAC</td></tr>
<tr><td>Hash</td><td>SHA-256, SHA-3, BLAKE2/3</td>
<td>MD5, SHA-1</td></tr>
<tr><td>KDF (password)</td><td>Argon2id, scrypt, bcrypt</td>
<td>plain MD5/SHA1, low-cost PBKDF2</td></tr>
<tr><td>Asymmetric key</td><td>Ed25519, X25519, ECDSA P-256, RSA-3072+</td>
<td>RSA-1024, DSA</td></tr>
<tr><td>TLS</td><td>TLS 1.3 (preferred), 1.2 OK</td>
<td>TLS 1.0/1.1, SSLv3, SSLv2</td></tr>
</table>

<h3>4. KMS, key management as a service</h3>
<p>KMS solves the critical problem of where to actually store the
key — instead of a file on the application's own disk, it lives
inside a managed HSM (Hardware Security Module), a dedicated chip
certified FIPS 140-2 Level 2 or 3, from which the key NEVER leaves in
plain text. The application interacts with it via an encrypt/decrypt
API — it sends the plain text, receives the ciphertext, without ever
handling the key directly. Every use of that key is logged in
CloudTrail for full auditing. Rotation happens automatically
(annually, for a managed CMK). And deleting the key deliberately
makes the data protected by it inaccessible — with a waiting window
of 7 to 30 days to reverse an accidental deletion before it becomes
permanent. KMS also allows cross-account configuration: a bucket in
account A encrypted by a key managed in account B, a deliberate
separation of power where compromising one account doesn't
automatically grant access to the other's key.</p>

<h3>5. Envelope encryption, at scale</h3>
<p>Calling KMS directly for every block of a terabyte of data would
be absurdly inefficient — the correct pattern is envelope encryption,
in four steps. First, the application requests a
<strong>data key</strong> from KMS: it generates a random AES-256
key, encrypts that same key with the CMK, and returns BOTH versions —
plaintext and encrypted. Second, the application uses the plaintext
version of that data key to encrypt the actual data locally, at the
normal speed of a symmetric cipher. Third, the application stores
only <code>{ciphertext_data, encrypted_data_key}</code> together — the
plaintext version of the data key is discarded immediately after use,
never persisted. To decrypt later, the process reverses: it asks KMS
to decrypt the <code>encrypted_data_key</code>, receives the
plaintext version back, and uses it to decrypt the actual data. The
result is that the MASTER key never leaves the HSM at any point,
while the data key specific to each piece of data is stored alongside
it — gaining local cipher performance without giving up the
centralized security of the master key:</p>
<pre><code>import boto3, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

kms = boto3.client('kms')

# Gerar data key
resp = kms.generate_data_key(KeyId='alias/my-cmk', KeySpec='AES_256')
plaintext_key = resp['Plaintext']
encrypted_key = resp['CiphertextBlob']    # armazenar com o dado

# Cifrar com AES-GCM (autenticada)
aes = AESGCM(plaintext_key)
nonce = os.urandom(12)
ciphertext = aes.encrypt(nonce, b'dados sensiveis', associated_data=b'tenant-x')

# Para decifrar:
plaintext_key = kms.decrypt(CiphertextBlob=encrypted_key)['Plaintext']
data = AESGCM(plaintext_key).decrypt(nonce, ciphertext, b'tenant-x')</code></pre>

<h3>6. TLS 1.3, the best way to do it</h3>
<p>TLS 1.3 solved four structural problems from earlier versions: the
handshake dropped to 1 round-trip (versus 2 in TLS 1.2), with 0-RTT
available on a resumed session, reducing perceived latency on the
initial connection; forward secrecy became MANDATORY, with only ECDHE
allowed — even if the server's private key leaks in the future,
captured past traffic remains undecipherable; legacy cipher suites
(RC4, MD5, SHA1) were removed completely from the protocol, with no
fallback option; and renegotiation, which was historically a known
attack vector, was eliminated for good. A minimal "modern"
configuration (Mozilla's recommendation) looks like this:</p>
<pre><code>ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;</code></pre>
<p>Auditing the final configuration on SSL Labs, aiming for an A+
grade, confirms that no detail was left out of that combination.</p>

<h3>7. mTLS, mutual authentication</h3>
<p>A regular TLS connection only verifies the SERVER, via a
certificate — the client remains anonymous from a cryptographic
standpoint. mTLS flips part of that: the server ALSO verifies the
client, creating authentication in both directions. The typical use
case is service-to-service communication inside a mesh, where each
service carries its own certificate issued by an internal CA. In
Kubernetes, a service mesh (Istio, Linkerd) automates this entirely:
each Pod receives a certificate via SPIFFE, with rotation every 24
hours and automatic validation — the result is genuine cryptographic
authentication between internal services, without needing to change a
single line of the application's own code.</p>

<h3>8. Password hashing is not encryption</h3>
<p>Hashing is one-way by definition — given the result, there is no
path back to the original password. But plain SHA-256 doesn't work
for passwords: an attacker with a GPU tries billions of combinations
per second against a hash that's too simple. The correct alternative
is a purpose-built KDF, designed to be DELIBERATELY slow and
expensive to parallelize: Argon2id won the Password Hashing
Competition in 2015 and is memory-hard, making GPU parallelization
expensive even with dedicated hardware, with tunable memory cost,
iteration, and parallelism parameters; bcrypt remains an acceptable
classic option with a cost factor above 12; and scrypt offers the
same memory-hard property as Argon2:</p>
<pre><code>from argon2 import PasswordHasher
ph = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)
hashed = ph.hash('senha-do-usuario')
# salva 'hashed' no banco
ph.verify(hashed, 'senha-do-usuario')</code></pre>
<p>Adding a salt is still essential (Argon2 and bcrypt already do
this automatically) — without a salt, an attacker solves the entire
hash at once with a precomputed rainbow table, instead of having to
attack each password individually.</p>

<h3>9. Post-quantum: what's coming</h3>
<p>A quantum computer with enough qubits will break RSA and ECC via
Shor's algorithm — the current estimate is somewhere between 10 and
20 years before that becomes practical. The real problem, though,
predates that date: data encrypted TODAY and captured by an attacker
can be decrypted in the future as soon as that capability exists —
the so-called "harvest now, decrypt later" attack is already
happening right now, even though the quantum computer capable of
completing the decryption doesn't exist yet. NIST published the first
official post-quantum standards in 2024: ML-KEM (Kyber, for key
exchange) and ML-DSA (Dilithium, for signing). Cloudflare, Google,
and AWS already offer optional hybrid TLS, combining the classical
algorithm with the post-quantum one at the same time — it's worth
considering this already for any data whose confidentiality value
extends more than ten years into the future.</p>

<h3>10. Real case: ROCA, keys broken en masse</h3>
<p>In 2017, researchers discovered that a library from Infineon —
used in smart cards and TPM modules widely distributed — generated
RSA-2048 keys with a specific mathematical weakness, allowing key
factorization at an estimated cost of around US$ 38 thousand in
rented cloud processing. The practical result was the need to rotate
government keys (including the whole of Estonia), corporate keys, and
millions of individual smart cards around the world. The direct
lessons: nominal key size (2048 bits) alone is not enough — the
IMPLEMENTATION that generates the key matters just as much as the
declared size; using an already widely audited library (OpenSSL,
libsodium, BoringSSL) drastically reduces this specific risk of
flawed generation; a key rotation mechanism needs to exist from day
one, not be added after an incident; and an HSM with updatable
firmware becomes a real advantage when a flaw of this kind is
discovered years after the original deployment.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Password in SHA-256 without salt or KDF</strong>: exactly
the mistake section 8 exists to fix.</li>
<li><strong>Static key hard-coded in the source code</strong>: anyone
with access to the repository extracts the key immediately.</li>
<li><strong>TLS with a self-signed certificate in production</strong>:
eliminates the identity guarantee that TLS exists to provide in the
first place.</li>
<li><strong>Outdated OpenSSL version</strong>: keeps a known old CVE
active by choice, not by accident.</li>
<li><strong>HSTS without <code>includeSubDomains</code> and without
<code>preload</code></strong>: leaves a subdomain or the first visit
outside full protection.</li>
<li><strong>Symmetric cipher without authentication</strong>
(AES-CBC without MAC): allows ciphertext tampering without
detection.</li>
<li><strong>Reused IV or nonce</strong>: breaks the security guarantee
of practically any modern cipher that depends on it being unique.</li>
<li><strong>Encryption at rest without encryption in transit</strong>:
protects data at a standstill but leaves that same data exposed
exactly when it travels over the network.</li>
<li><strong>"We encrypted the data" but the key sits on the same
disk</strong>: completely negates the purpose of encryption — whoever
steals the disk steals the key along with it.</li>
</ul>"""
                ),
                "practical": (
                    "(1) Crie uma CMK em KMS com rotação anual habilitada. Adicione policy "
                    "permitindo apenas uma role específica usar para encrypt/decrypt.<br>"
                    "(2) Use <code>aws kms encrypt</code> e <code>decrypt</code> via CLI "
                    "para entender o fluxo. Veja o log no CloudTrail.<br>"
                    "(3) Habilite encryption padrão SSE-KMS com sua CMK em um bucket S3. "
                    "Faça upload de um objeto e tente baixá-lo de uma role <em>sem</em> "
                    "permissão na CMK, deve falhar mesmo com S3 GetObject.<br>"
                    "(4) Em uma app Python, implemente envelope encryption com a CMK + "
                    "AES-GCM local.<br>"
                    "(5) Configure um Nginx com TLS 1.3 'modern' (Mozilla generator) e "
                    "audite com SSL Labs até A+.<br>"
                    "(6) Bônus: implemente hash de senha com Argon2id em uma rota "
                    "<code>/register</code>. Compare o tempo de hash com SHA-256 puro."
                ),
                "practical_en": (
                    "(1) Create a CMK in KMS with annual rotation enabled. Add a policy "
                    "allowing only a specific role to use it for encrypt/decrypt.<br>"
                    "(2) Use <code>aws kms encrypt</code> and <code>decrypt</code> via the CLI "
                    "to understand the flow. Check the log in CloudTrail.<br>"
                    "(3) Enable default SSE-KMS encryption with your CMK on an S3 bucket. "
                    "Upload an object and try to download it from a role <em>without</em> "
                    "permission on the CMK, it should fail even with S3 GetObject.<br>"
                    "(4) In a Python app, implement envelope encryption with the CMK + "
                    "local AES-GCM.<br>"
                    "(5) Configure an Nginx with 'modern' TLS 1.3 (Mozilla generator) and "
                    "audit it with SSL Labs until you reach A+.<br>"
                    "(6) Bonus: implement password hashing with Argon2id on a "
                    "<code>/register</code> route. Compare the hash time with plain SHA-256."
                ),
            },
            "materials": [
                m("AWS KMS",
                  "https://docs.aws.amazon.com/kms/latest/developerguide/", "docs", "",
                  title_en="AWS KMS", description_en=""),
                m("Azure Key Vault",
                  "https://learn.microsoft.com/azure/key-vault/general/overview", "docs", "",
                  title_en="Azure Key Vault", description_en=""),
                m("GCP Cloud KMS",
                  "https://cloud.google.com/kms/docs", "docs", "",
                  title_en="GCP Cloud KMS", description_en=""),
                m("Mozilla TLS Guidelines",
                  "https://wiki.mozilla.org/Security/Server_Side_TLS", "docs", "",
                  title_en="Mozilla TLS Guidelines", description_en=""),
                m("Cloudflare: SSL/TLS",
                  "https://www.cloudflare.com/learning/ssl/transport-layer-security-tls/",
                  "article", "",
                  title_en="Cloudflare: SSL/TLS", description_en=""),
                m("OWASP Cryptographic Storage Cheatsheet",
                  "https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html",
                  "docs", "",
                  title_en="OWASP Cryptographic Storage Cheat Sheet", description_en=""),
            ],
            "questions": [
                q("AES-256 é simétrica ou assimétrica?",
                  "Simétrica.",
                  ["Assimétrica.", "Sem chave.", "Quântica."],
                  "Mesma chave cifra/decifra. Por isso a chave nunca pode vazar.",
                  statement_en="Is AES-256 symmetric or asymmetric?",
                  correct_en="Symmetric.",
                  wrong_en=["Asymmetric.", "Keyless.", "Quantum."],
                  explanation_en="The same key encrypts and decrypts. That's why the key must never leak."),
                q("TLS depende de:",
                  "Certificado X.509 e chave privada.",
                  ["Só o endereço IP do servidor, sem verificação de identidade.",
                   "Só a regra de firewall liberando a porta 443, sem certificado.",
                   "Só a resolução de nome feita pelo DNS antes da conexão."],
                  "Cliente verifica o certificado contra CAs confiáveis; servidor prova posse da chave privada.",
                  statement_en="TLS depends on:",
                  correct_en="An X.509 certificate and a private key.",
                  wrong_en=["The server's IP address, with no identity check performed at all.",
                            "A firewall rule opening port 443, without any certificate involved.",
                            "The DNS name resolution completed before the connection starts."],
                  explanation_en="The client checks the certificate against trusted CAs; the server proves it holds the private key."),
                q("Por que rotacionar chaves KMS?",
                  "Reduz impacto de eventual comprometimento.",
                  ["Um requisito real do protocolo HTTP sem criptografia.",
                   "Reduz o custo mensal cobrado pelo uso do serviço de chave.",
                   "Aumenta a velocidade de resposta da chamada de API feita."],
                  "KMS rotaciona automaticamente em CMKs gerenciadas (anual). Re-criptografa lazy ao acessar.",
                  statement_en="Why rotate KMS keys?",
                  correct_en="It reduces the impact of a potential compromise.",
                  wrong_en=["An actual requirement of the unencrypted HTTP protocol itself.",
                            "It reduces the monthly cost charged for using the key service.",
                            "It increases the response speed of the API call being made."],
                  explanation_en="KMS rotates automatically on managed CMKs (yearly). It re-encrypts lazily on access."),
                q("HSM serve para:",
                  "Armazenar chaves criptográficas em hardware dedicado.",
                  ["Criar política de acesso dentro do IAM da própria conta AWS.",
                   "Substituir por completo a necessidade de configurar IAM na conta.",
                   "Comprimir o dado antes de armazená-lo fisicamente em disco."],
                  "HSMs têm certificações (FIPS 140-3 Level 3) e impedem extração da chave.",
                  statement_en="An HSM is used for:",
                  correct_en="Storing cryptographic keys in dedicated hardware.",
                  wrong_en=["Creating an access policy inside the AWS account's own IAM.",
                            "Completely replacing the need to configure IAM on the account.",
                            "Compressing the data before physically storing it on disk."],
                  explanation_en="HSMs carry certifications (FIPS 140-3 Level 3) and prevent key extraction."),
                q("Algoritmo recomendado para hash de senha:",
                  "Argon2 ou bcrypt com custo alto.",
                  ["SHA-1, hash rápido demais e já quebrado por colisão.",
                   "Base64, só uma codificação reversível, não um hash de verdade.",
                   "MD5, hash antigo e vulnerável a ataque de força bruta rápido."],
                  "Argon2 ganhou a Password Hashing Competition. bcrypt continua aceitável.",
                  statement_en="Recommended algorithm for password hashing:",
                  correct_en="Argon2 or bcrypt with a high cost factor.",
                  wrong_en=["SHA-1, a hash that's too fast and already broken by collision attacks.",
                            "Base64, just a reversible encoding, not a real hash at all.",
                            "MD5, an old hash algorithm vulnerable to fast brute-force attacks."],
                  explanation_en="Argon2 won the Password Hashing Competition. bcrypt remains acceptable."),
                q("Forward secrecy garante:",
                  "Que comprometimento da chave atual não revele tráfego antigo.",
                  ["Uma velocidade de handshake maior do que a versão anterior do protocolo.",
                   "Um backup automático da chave de sessão usada na conexão.",
                   "Compatibilidade retroativa com o antigo e inseguro SSLv2."],
                  "ECDHE gera chave de sessão efêmera. Sem forward secrecy, atacante guarda tráfego "
                  "para descriptografar quando obtiver a chave.",
                  statement_en="Forward secrecy guarantees:",
                  correct_en="That compromising the current key does not reveal previously captured traffic.",
                  wrong_en=["A faster handshake speed compared to the protocol's previous version.",
                            "An automatic backup of the session key used in the connection.",
                            "Backward compatibility with the old and insecure SSLv2 protocol."],
                  explanation_en="ECDHE generates an ephemeral session key. Without forward secrecy, an attacker "
                  "stores traffic to decrypt once they obtain the key."),
                q("HSTS é mecanismo de:",
                  "Força HTTPS em browsers.",
                  ["Roteamento de pacote entre duas redes distintas.",
                   "Backup periódico do certificado emitido pela CA.",
                   "Criptografia de dado parado em disco, não em trânsito."],
                  "Header HTTP que diz: 'sempre acesse este host por HTTPS pelos próximos N segundos'.",
                  statement_en="HSTS is a mechanism for:",
                  correct_en="Forcing HTTPS in browsers.",
                  wrong_en=["Routing packets between two distinct networks.",
                            "Periodic backup of the certificate issued by the CA.",
                            "Encrypting data at rest on disk, not in transit."],
                  explanation_en="An HTTP header that says: 'always reach this host over HTTPS for the next N seconds'."),
                q("Certificate Authority (CA) confiável é necessária para:",
                  "Que clientes confiem no certificado sem warning.",
                  ["Aumentar a performance de resposta do servidor web.",
                   "Servir conteúdo em HTTP puro, sem qualquer camada de TLS envolvida.",
                   "Comprimir dado antes de enviar pela rede ao cliente."],
                  "Em produção pública use Let's Encrypt/ACM/etc. Em interno, considere CA privada (Vault, AWS PCA).",
                  statement_en="A trusted Certificate Authority (CA) is necessary for:",
                  correct_en="Having clients trust the certificate without a warning.",
                  wrong_en=["Increasing the response performance of the web server.",
                            "Serving content over plain HTTP, with no TLS layer involved.",
                            "Compressing data before sending it over the network to the client."],
                  explanation_en="In public production use Let's Encrypt/ACM/etc. Internally, consider a private CA (Vault, AWS PCA)."),
                q("Vazou a chave privada do TLS, deve-se:",
                  "Revogar e rotacionar imediatamente.",
                  ["Manter em uso por compatibilidade com cliente antigo.",
                   "Abrir um chamado de SLA com o provedor de certificado.",
                   "Apagar log antigo relacionado ao uso daquela chave."],
                  "Tráfego antigo pode ser descriptografado se não houver forward secrecy. Revogue via CRL/OCSP.",
                  statement_en="If the TLS private key leaks, you should:",
                  correct_en="Revoke and rotate it immediately.",
                  wrong_en=["Keep it in use for compatibility with an older client.",
                            "Open an SLA ticket with the certificate provider.",
                            "Delete old logs related to the use of that key."],
                  explanation_en="Old traffic can be decrypted if there's no forward secrecy. Revoke it via CRL/OCSP."),
                q("'Encryption at rest' protege:",
                  "Dados armazenados em disco.",
                  ["Só o dado que está temporariamente na memória RAM.",
                   "Só a resolução de nome feita pelo servidor de DNS.",
                   "Tráfego trafegando entre dois servidores diferentes."],
                  "Mitiga roubo de disco/snapshot. Não protege se atacante já tem acesso lógico ao recurso.",
                  statement_en="'Encryption at rest' protects:",
                  correct_en="Data stored on disk.",
                  wrong_en=["Data temporarily sitting in RAM memory, not on disk.",
                            "The name resolution performed by the DNS server, unrelated to storage.",
                            "Traffic traveling between two different servers, not data at rest."],
                  explanation_en="Mitigates disk/snapshot theft. Doesn't protect if the attacker already has logical access to the resource."),
            ],
        },
        # =====================================================================
        # 2.8 Monitoramento Básico
        # =====================================================================
        {
            "title": "Monitoramento Básico (CloudWatch/Monitor)",
            "title_en": "Basic Monitoring (CloudWatch/Monitor)",
            "summary": "Saber se o servidor está vivo e saudável.",
            "summary_en": "Knowing whether the server is alive and healthy.",
            "lesson": {
                "intro": (
                    "Sem monitoramento, deploy é fé e produção é roleta. Mas monitoramento "
                    "ruim é tão pernicioso quanto: dashboards com 200 gráficos que ninguém "
                    "olha, alertas que disparam toda hora e ninguém atende, métricas que "
                    "não medem o que importa para o usuário.<br><br>"
                    "Esta aula segue a abordagem do Google SRE Book: foco nas poucas "
                    "métricas que importam, SLO/SLI/SLA, error budget, alertas baseados em "
                    "burn rate e a tríade observabilidade (métricas + logs + traces). É a "
                    "base para qualquer time que queira sair do modo 'apaga incêndio' e "
                    "entrar no modo 'engineer reliability'."
                ),
                "intro_en": (
                    "Without monitoring, deploying is an act of faith and production is "
                    "roulette. But bad monitoring is just as harmful: dashboards with 200 "
                    "graphs nobody looks at, alerts that fire all the time and nobody "
                    "handles, metrics that don't measure what matters to the user.<br><br>"
                    "This lesson follows the approach of the Google SRE Book: focus on the "
                    "few metrics that matter, SLO/SLI/SLA, error budget, burn-rate-based "
                    "alerts, and the observability triad (metrics + logs + traces). It's the "
                    "foundation for any team that wants to move out of 'firefighting' mode "
                    "and into 'engineering reliability' mode."
                ),
                "body": (
                    "<h3>1. Os 4 sinais de ouro (Google SRE)</h3>"
                    "<p>De todas as métricas que você pode coletar, 4 dizem se um serviço "
                    "está bem ou mal:</p>"
                    """
<div class="mermaid">
flowchart LR
    App["Aplicação / infra"] --> Metric["Métrica coletada"]
    Metric --> Threshold{"Ultrapassou o limite configurado?"}
    Threshold -- "Sim" --> Alert["Dispara alerta"]
    Threshold -- "Não" --> Metric
</div>
"""
                    "<ol>"
                    "<li><strong>Latência</strong>: tempo de resposta. Separe sucesso "
                    "(p50, p99) de erro (latência de 5xx pode ser baixa por timeout rápido, "
                    "esconde o problema).</li>"
                    "<li><strong>Tráfego</strong>: requisições/seg, bytes/seg, mensagens "
                    "consumidas/seg.</li>"
                    "<li><strong>Erros</strong>: taxa de falha. Para HTTP, 5xx (erro do "
                    "servidor) e 4xx específicos (429, 401 quando não esperado).</li>"
                    "<li><strong>Saturação</strong>: quão cheio o sistema está. CPU, memória, "
                    "fila de mensagens, conexões DB. Saturação alta = dor próxima.</li>"
                    "</ol>"
                    "<p>Outros frameworks que aparecem na literatura:</p>"
                    "<ul>"
                    "<li><strong>RED</strong> (Rate, Errors, Duration): para serviços "
                    "request-driven.</li>"
                    "<li><strong>USE</strong> (Utilization, Saturation, Errors): para "
                    "recursos (CPU, disco, NIC).</li>"
                    "</ul>"

                    "<h3>2. SLI, SLO, SLA, vocabulário comum</h3>"
                    "<table>"
                    "<tr><th>Termo</th><th>O que é</th><th>Exemplo</th></tr>"
                    "<tr><td><strong>SLI</strong></td><td>Service Level Indicator: a medida</td>"
                    "<td>'% de respostas em &lt;200ms'</td></tr>"
                    "<tr><td><strong>SLO</strong></td><td>Service Level Objective: o objetivo "
                    "interno</td><td>'99,9% no mês'</td></tr>"
                    "<tr><td><strong>SLA</strong></td><td>Service Level Agreement: contrato "
                    "com cliente, com penalidades</td><td>'99,5% mensal, abaixo, 5% de "
                    "desconto'</td></tr>"
                    "</table>"
                    "<p>SLA &lt; SLO sempre. Você quer error budget para gastar em deploys "
                    "antes de violar contrato.</p>"

                    "<h3>3. Error budget e burn rate</h3>"
                    "<p>Error budget = (1 − SLO) por período. Se SLO é 99,9% mensal:</p>"
                    "<ul>"
                    "<li>Budget = 0,1% × 30d × 24h × 60min ≈ 43,2 minutos de erro/mês.</li>"
                    "<li>Cada minuto de outage 'gasta' 1 minuto do budget.</li>"
                    "<li>Quando budget acaba: paralise releases, foque em estabilidade.</li>"
                    "<li>Quando sobra: tome mais riscos, libere features.</li>"
                    "</ul>"
                    "<p>Esta é a peça-chave que alinha dev e SRE: tem orçamento técnico "
                    "compartilhado, não é mais 'time A quer estabilidade, time B quer "
                    "velocidade'.</p>"
                    "<p><strong>Burn rate alerts</strong> são os bons:</p>"
                    "<pre><code># Em 1h gastamos 2% do budget mensal? Burn rate = 14.4x normal.\n"
                    "# Alarme \"page\", incidente em curso.\n"
                    "ALERT FastBurn\n"
                    "  IF (slo:error_budget_burn:rate1h > 14.4)\n"
                    "  AND (slo:error_budget_burn:rate5m > 14.4)\n"
                    "\n"
                    "# Em 6h gastamos 5% do budget? Burn rate = 6x normal.\n"
                    "# Alarme \"ticket\", investigar hoje.\n"
                    "ALERT SlowBurn\n"
                    "  IF (slo:error_budget_burn:rate6h > 6)</code></pre>"

                    "<h3>4. Histogramas e percentis</h3>"
                    "<p>'A latência média da API é 50ms' é a frase mais perigosa em "
                    "operação. Média esconde a cauda:</p>"
                    "<pre><code>1000 requests:\n"
                    "  990 em 20ms  (rápido)\n"
                    "  10  em 3000ms (timeouts)\n"
                    "  Média = (990*20 + 10*3000) / 1000 = 49.8ms  ← parece OK\n"
                    "  P99   = 3000ms                              ← realidade</code></pre>"
                    "<p>Use <strong>histogramas</strong>:</p>"
                    "<pre><code># Prometheus\n"
                    "http_request_duration_seconds_bucket{le=\"0.05\"}  3490\n"
                    "http_request_duration_seconds_bucket{le=\"0.1\"}   3700\n"
                    "http_request_duration_seconds_bucket{le=\"0.5\"}   3950\n"
                    "http_request_duration_seconds_bucket{le=\"1.0\"}   3980\n"
                    "http_request_duration_seconds_bucket{le=\"+Inf\"}  4000\n"
                    "\n"
                    "# Calcula p99 sobre 5min\n"
                    "histogram_quantile(0.99,\n"
                    "  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)\n"
                    ")</code></pre>"
                    "<p>Reporte sempre p50 (mediana), p95 e p99. Use p99 (ou p99.9 em apps "
                    "críticas) como SLI.</p>"

                    "<h3>5. Stack típica em K8s/cloud</h3>"
                    "<table>"
                    "<tr><th>Sinal</th><th>Stack</th><th>Alternativas</th></tr>"
                    "<tr><td>Métricas</td><td>Prometheus + Grafana</td>"
                    "<td>VictoriaMetrics, Mimir, CloudWatch, Datadog</td></tr>"
                    "<tr><td>Logs</td><td>Loki + Grafana</td>"
                    "<td>ELK, OpenSearch, CloudWatch Logs</td></tr>"
                    "<tr><td>Traces</td><td>Tempo + Grafana</td>"
                    "<td>Jaeger, Zipkin, X-Ray</td></tr>"
                    "<tr><td>Alertas</td><td>Alertmanager + PagerDuty/Opsgenie</td>"
                    "<td>VictorOps, OpsLevel</td></tr>"
                    "<tr><td>Coletor</td><td>OpenTelemetry Collector</td>"
                    "<td>Vector, Fluent Bit, Promtail</td></tr>"
                    "</table>"
                    "<p>OpenTelemetry está virando o padrão único para instrumentação, "
                    "instrumente uma vez, troque o backend depois.</p>"

                    "<h3>6. Cardinalidade, o assassino silencioso</h3>"
                    "<p>Cada combinação de labels em uma métrica é uma série temporal "
                    "armazenada. Se você tem:</p>"
                    "<ul>"
                    "<li>10 endpoints (low cardinality)</li>"
                    "<li>5 status codes (low)</li>"
                    "<li>3 regiões (low)</li>"
                    "</ul>"
                    "<p>= 150 séries. Saudável.</p>"
                    "<p>Mas se você adicionar:</p>"
                    "<ul>"
                    "<li><code>user_id</code> com 1M usuários (HIGH)</li>"
                    "</ul>"
                    "<p>= 150M séries. Backend explode em RAM e cobrança.</p>"
                    "<p>Regra: <strong>IDs vão em logs/traces, não em métricas</strong>. "
                    "Métricas são para agregados; trace lhe dá detalhe da request "
                    "específica.</p>"

                    "<h3>7. Alertas que não viram fadiga</h3>"
                    "<p>Cada alerta deve passar no teste do plantão:</p>"
                    "<blockquote>'Se isto disparar às 3h da manhã, o que devo fazer?'</blockquote>"
                    "<p>Se a resposta é 'nada urgente', não é alerta, é métrica de dashboard.</p>"
                    "<p>Princípios:</p>"
                    "<ul>"
                    "<li>Alarme em SLO violado, não em CPU 80%.</li>"
                    "<li>Burn rate &gt; threshold (não 'erro &gt; 5').</li>"
                    "<li>Toda alarme tem runbook anexo (link no payload).</li>"
                    "<li>Severidade clara: page (acorde alguém) vs ticket (investigar de "
                    "manhã).</li>"
                    "<li>Revisão mensal: alarme que não disparou mas é crítico = bug? "
                    "Alarme que disparou e foi falso = remova ou ajuste.</li>"
                    "</ul>"

                    "<h3>8. Métricas operacionais vs métricas de negócio</h3>"
                    "<p>Não monitore só CPU. Monitore o <em>negócio</em>:</p>"
                    "<ul>"
                    "<li>Pedidos/min (queda súbita = problema).</li>"
                    "<li>Taxa de checkout completado.</li>"
                    "<li>Login fail rate.</li>"
                    "<li>Conversão de signup.</li>"
                    "</ul>"
                    "<p>Em 2018, GitLab teve outage de banco. Alarmes de infra dispararam. "
                    "Mas o que mostrou impacto real foi 'pushes/min caindo a zero', "
                    "métrica de produto. Tenha as duas.</p>"

                    "<h3>9. SLOs típicos por tipo de serviço</h3>"
                    "<table>"
                    "<tr><th>Tipo</th><th>SLO típico</th><th>Downtime/mês</th></tr>"
                    "<tr><td>API consumer-facing</td><td>99,9%</td><td>43 min</td></tr>"
                    "<tr><td>API internal</td><td>99%</td><td>7,2 h</td></tr>"
                    "<tr><td>Batch / async</td><td>SLI = % completados em X horas</td>"
                    "<td>-</td></tr>"
                    "<tr><td>Pagamento crítico</td><td>99,99%</td><td>4,3 min</td></tr>"
                    "<tr><td>Coisa de dev (CI)</td><td>99%</td><td>7,2 h</td></tr>"
                    "</table>"
                    "<p>4 noves é caro: exige multi-region, tudo redundado. 5 noves "
                    "(99,999%) é praticamente impossível em apps web, só serviços "
                    "muito simples.</p>"

                    "<h3>10. Caso real: o caso do dashboard sem dono</h3>"
                    "<p>Em uma fintech brasileira, em 2022, time descobriu durante incidente "
                    "que o dashboard 'master' tinha 73 painéis. Ninguém sabia o que "
                    "metade significava. Métricas inventadas pela pessoa que saiu da "
                    "empresa em 2019. Alarmes apontando para Slack channels que ninguém "
                    "monitorava.</p>"
                    "<p>Resultado: incidente passou 4h sem ser detectado, mesmo com "
                    "'monitoring completo'. Lição: monitoramento sem ownership e revisão "
                    "ativa é só armazenamento caro. Cada painel/alarme deve ter dono e "
                    "data de última revisão.</p>"
                ),
                "body_en": (
                    "<h3>1. The 4 golden signals (Google SRE)</h3>"
                    "<p>Of all the metrics you could collect, 4 tell you whether a service "
                    "is healthy or not:</p>"
                    """
<div class="mermaid">
flowchart LR
    App["Aplicação / infra"] --> Metric["Métrica coletada"]
    Metric --> Threshold{"Ultrapassou o limite configurado?"}
    Threshold -- "Sim" --> Alert["Dispara alerta"]
    Threshold -- "Não" --> Metric
</div>
"""
                    "<ol>"
                    "<li><strong>Latency</strong>: response time. Separate success "
                    "(p50, p99) from error (5xx latency can be low due to a quick timeout, "
                    "which hides the problem).</li>"
                    "<li><strong>Traffic</strong>: requests/sec, bytes/sec, messages "
                    "consumed/sec.</li>"
                    "<li><strong>Errors</strong>: failure rate. For HTTP, 5xx (server "
                    "error) and specific 4xx (429, 401 when unexpected).</li>"
                    "<li><strong>Saturation</strong>: how full the system is. CPU, memory, "
                    "message queue, DB connections. High saturation = pain approaching.</li>"
                    "</ol>"
                    "<p>Other frameworks that show up in the literature:</p>"
                    "<ul>"
                    "<li><strong>RED</strong> (Rate, Errors, Duration): for "
                    "request-driven services.</li>"
                    "<li><strong>USE</strong> (Utilization, Saturation, Errors): for "
                    "resources (CPU, disk, NIC).</li>"
                    "</ul>"

                    "<h3>2. SLI, SLO, SLA, common vocabulary</h3>"
                    "<table>"
                    "<tr><th>Term</th><th>What it is</th><th>Example</th></tr>"
                    "<tr><td><strong>SLI</strong></td><td>Service Level Indicator: the measurement</td>"
                    "<td>'% of responses under 200ms'</td></tr>"
                    "<tr><td><strong>SLO</strong></td><td>Service Level Objective: the internal "
                    "target</td><td>'99.9% for the month'</td></tr>"
                    "<tr><td><strong>SLA</strong></td><td>Service Level Agreement: contract "
                    "with the customer, with penalties</td><td>'99.5% monthly, below that, 5% "
                    "discount'</td></tr>"
                    "</table>"
                    "<p>SLA is always &lt; SLO. You want error budget to spend on deploys "
                    "before breaching the contract.</p>"

                    "<h3>3. Error budget and burn rate</h3>"
                    "<p>Error budget = (1 − SLO) per period. If the SLO is 99.9% monthly:</p>"
                    "<ul>"
                    "<li>Budget = 0.1% × 30d × 24h × 60min ≈ 43.2 minutes of error/month.</li>"
                    "<li>Every minute of outage 'spends' 1 minute of the budget.</li>"
                    "<li>When the budget runs out: freeze releases, focus on stability.</li>"
                    "<li>When there's a surplus: take more risks, ship features.</li>"
                    "</ul>"
                    "<p>This is the key piece that aligns dev and SRE: there's a shared "
                    "technical budget, it's no longer 'team A wants stability, team B wants "
                    "speed'.</p>"
                    "<p><strong>Burn rate alerts</strong> are the good ones:</p>"
                    "<pre><code># Em 1h gastamos 2% do budget mensal? Burn rate = 14.4x normal.\n"
                    "# Alarme \"page\", incidente em curso.\n"
                    "ALERT FastBurn\n"
                    "  IF (slo:error_budget_burn:rate1h > 14.4)\n"
                    "  AND (slo:error_budget_burn:rate5m > 14.4)\n"
                    "\n"
                    "# Em 6h gastamos 5% do budget? Burn rate = 6x normal.\n"
                    "# Alarme \"ticket\", investigar hoje.\n"
                    "ALERT SlowBurn\n"
                    "  IF (slo:error_budget_burn:rate6h > 6)</code></pre>"

                    "<h3>4. Histograms and percentiles</h3>"
                    "<p>'The API's average latency is 50ms' is the most dangerous sentence in "
                    "operations. Averages hide the tail:</p>"
                    "<pre><code>1000 requests:\n"
                    "  990 em 20ms  (rápido)\n"
                    "  10  em 3000ms (timeouts)\n"
                    "  Média = (990*20 + 10*3000) / 1000 = 49.8ms  ← parece OK\n"
                    "  P99   = 3000ms                              ← realidade</code></pre>"
                    "<p>Use <strong>histograms</strong>:</p>"
                    "<pre><code># Prometheus\n"
                    "http_request_duration_seconds_bucket{le=\"0.05\"}  3490\n"
                    "http_request_duration_seconds_bucket{le=\"0.1\"}   3700\n"
                    "http_request_duration_seconds_bucket{le=\"0.5\"}   3950\n"
                    "http_request_duration_seconds_bucket{le=\"1.0\"}   3980\n"
                    "http_request_duration_seconds_bucket{le=\"+Inf\"}  4000\n"
                    "\n"
                    "# Calcula p99 sobre 5min\n"
                    "histogram_quantile(0.99,\n"
                    "  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)\n"
                    ")</code></pre>"
                    "<p>Always report p50 (median), p95, and p99. Use p99 (or p99.9 in "
                    "critical apps) as the SLI.</p>"

                    "<h3>5. Typical stack in K8s/cloud</h3>"
                    "<table>"
                    "<tr><th>Signal</th><th>Stack</th><th>Alternatives</th></tr>"
                    "<tr><td>Metrics</td><td>Prometheus + Grafana</td>"
                    "<td>VictoriaMetrics, Mimir, CloudWatch, Datadog</td></tr>"
                    "<tr><td>Logs</td><td>Loki + Grafana</td>"
                    "<td>ELK, OpenSearch, CloudWatch Logs</td></tr>"
                    "<tr><td>Traces</td><td>Tempo + Grafana</td>"
                    "<td>Jaeger, Zipkin, X-Ray</td></tr>"
                    "<tr><td>Alerts</td><td>Alertmanager + PagerDuty/Opsgenie</td>"
                    "<td>VictorOps, OpsLevel</td></tr>"
                    "<tr><td>Collector</td><td>OpenTelemetry Collector</td>"
                    "<td>Vector, Fluent Bit, Promtail</td></tr>"
                    "</table>"
                    "<p>OpenTelemetry is becoming the single standard for instrumentation, "
                    "instrument once, swap the backend later.</p>"

                    "<h3>6. Cardinality, the silent killer</h3>"
                    "<p>Every combination of labels on a metric is a stored time series. "
                    "If you have:</p>"
                    "<ul>"
                    "<li>10 endpoints (low cardinality)</li>"
                    "<li>5 status codes (low)</li>"
                    "<li>3 regions (low)</li>"
                    "</ul>"
                    "<p>= 150 series. Healthy.</p>"
                    "<p>But if you add:</p>"
                    "<ul>"
                    "<li><code>user_id</code> with 1M users (HIGH)</li>"
                    "</ul>"
                    "<p>= 150M series. The backend explodes in RAM usage and billing.</p>"
                    "<p>Rule: <strong>IDs go in logs/traces, not in metrics</strong>. "
                    "Metrics are for aggregates; a trace gives you the detail of the "
                    "specific request.</p>"

                    "<h3>7. Alerts that don't turn into fatigue</h3>"
                    "<p>Every alert must pass the on-call test:</p>"
                    "<blockquote>'If this fires at 3am, what am I supposed to do?'</blockquote>"
                    "<p>If the answer is 'nothing urgent', it's not an alert, it's a dashboard "
                    "metric.</p>"
                    "<p>Principles:</p>"
                    "<ul>"
                    "<li>Alert on SLO violated, not on 80% CPU.</li>"
                    "<li>Burn rate &gt; threshold (not 'error &gt; 5').</li>"
                    "<li>Every alarm has an attached runbook (link in the payload).</li>"
                    "<li>Clear severity: page (wake someone up) vs ticket (investigate in "
                    "the morning).</li>"
                    "<li>Monthly review: an alarm that didn't fire but is critical = bug? "
                    "An alarm that fired and was false = remove or adjust it.</li>"
                    "</ul>"

                    "<h3>8. Operational metrics vs business metrics</h3>"
                    "<p>Don't just monitor CPU. Monitor the <em>business</em>:</p>"
                    "<ul>"
                    "<li>Orders/min (a sudden drop = problem).</li>"
                    "<li>Completed checkout rate.</li>"
                    "<li>Login fail rate.</li>"
                    "<li>Signup conversion.</li>"
                    "</ul>"
                    "<p>In 2018, GitLab had a database outage. Infra alarms fired. "
                    "But what showed the real impact was 'pushes/min dropping to zero', a "
                    "product metric. Have both.</p>"

                    "<h3>9. Typical SLOs by service type</h3>"
                    "<table>"
                    "<tr><th>Type</th><th>Typical SLO</th><th>Downtime/month</th></tr>"
                    "<tr><td>Consumer-facing API</td><td>99.9%</td><td>43 min</td></tr>"
                    "<tr><td>Internal API</td><td>99%</td><td>7.2 h</td></tr>"
                    "<tr><td>Batch / async</td><td>SLI = % completed within X hours</td>"
                    "<td>-</td></tr>"
                    "<tr><td>Critical payment</td><td>99.99%</td><td>4.3 min</td></tr>"
                    "<tr><td>Dev tooling (CI)</td><td>99%</td><td>7.2 h</td></tr>"
                    "</table>"
                    "<p>Four nines is expensive: it requires multi-region, everything "
                    "redundant. Five nines (99.999%) is practically impossible for web "
                    "apps, only for very simple services.</p>"

                    "<h3>10. Real case: the dashboard with no owner</h3>"
                    "<p>At a Brazilian fintech, in 2022, the team discovered during an "
                    "incident that the 'master' dashboard had 73 panels. Nobody knew what "
                    "half of them meant. Metrics invented by someone who had left the "
                    "company in 2019. Alarms pointing to Slack channels nobody "
                    "monitored.</p>"
                    "<p>Result: the incident went 4 hours without being detected, even with "
                    "'complete monitoring'. Lesson: monitoring without ownership and active "
                    "review is just expensive storage. Every panel/alarm should have an "
                    "owner and a last-reviewed date.</p>"
                ),
                "practical": (
                    "(1) Defina um SLO realístico para uma rota da sua app (ex.: "
                    "<code>GET /api/users</code>): '95% das requests respondem em &lt;300ms "
                    "com 200/4xx'.<br>"
                    "(2) Suba Prometheus + Grafana via docker-compose. Instrumente sua app "
                    "com OpenTelemetry (Python tem auto-instrumentation).<br>"
                    "(3) Crie no Grafana 4 painéis (golden signals): latência p50/p95/p99, "
                    "tráfego, erros, saturação (CPU).<br>"
                    "(4) Configure burn-rate alerts no Alertmanager (rate1h &gt; 14.4 = "
                    "page).<br>"
                    "(5) Para cada alarme, escreva runbook de 3 linhas: '1) verificar X; "
                    "2) se X=Y, fazer Z; 3) escalar para A se persistir'.<br>"
                    "(6) Bônus: simule outage (mata o container 5min) e veja burn rate "
                    "subir; alarme deve disparar."
                ),
                "practical_en": (
                    "(1) Define a realistic SLO for a route in your app (e.g.: "
                    "<code>GET /api/users</code>): '95% of requests respond in &lt;300ms "
                    "with 200/4xx'.<br>"
                    "(2) Spin up Prometheus + Grafana via docker-compose. Instrument your app "
                    "with OpenTelemetry (Python has auto-instrumentation).<br>"
                    "(3) Create 4 panels in Grafana (golden signals): p50/p95/p99 latency, "
                    "traffic, errors, saturation (CPU).<br>"
                    "(4) Configure burn-rate alerts in Alertmanager (rate1h &gt; 14.4 = "
                    "page).<br>"
                    "(5) For each alarm, write a 3-line runbook: '1) check X; "
                    "2) if X=Y, do Z; 3) escalate to A if it persists'.<br>"
                    "(6) Bonus: simulate an outage (kill the container for 5min) and watch "
                    "the burn rate climb; the alarm should fire."
                ),
            },
            "materials": [
                m("Google SRE: SLO, SLI, SLA",
                  "https://sre.google/sre-book/service-level-objectives/", "book", "",
                  title_en="Google SRE: SLO, SLI, SLA", description_en=""),
                m("AWS CloudWatch",
                  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
                  "docs", "",
                  title_en="AWS CloudWatch", description_en=""),
                m("Azure Monitor docs",
                  "https://learn.microsoft.com/azure/azure-monitor/overview", "docs", "",
                  title_en="Azure Monitor docs", description_en=""),
                m("Prometheus",
                  "https://prometheus.io/docs/introduction/overview/", "docs", "",
                  title_en="Prometheus", description_en=""),
                m("Grafana docs",
                  "https://grafana.com/docs/grafana/latest/", "docs", "",
                  title_en="Grafana docs", description_en=""),
                m("OpenTelemetry",
                  "https://opentelemetry.io/docs/", "docs",
                  "Padrão para instrumentação.",
                  title_en="OpenTelemetry", description_en="Standard for instrumentation."),
            ],
            "questions": [
                q("Os '4 golden signals' são:",
                  "Latência, tráfego, erros e saturação.",
                  ["CPU, RAM, disco e rede, métricas de infraestrutura básica.",
                   "Requisição por segundo, quadro por segundo, megabyte, milissegundo.",
                   "Estado de ligado ou desligado, sem qualquer outra dimensão medida."],
                  "Definidos pelo Google SRE Book. Cobrem as dimensões essenciais de qualquer serviço.",
                  statement_en="The '4 golden signals' are:",
                  correct_en="Latency, traffic, errors, and saturation.",
                  wrong_en=["CPU, RAM, disk, and network, basic infrastructure metrics.",
                            "Requests per second, frames per second, megabyte, millisecond.",
                            "On or off state, with no other dimension being measured."],
                  explanation_en="Defined by the Google SRE Book. They cover the essential dimensions of any service."),
                q("SLO mede:",
                  "Objetivo de qualidade de serviço (ex.: 99,9% de disponibilidade).",
                  ["Custo mensal total cobrado pela conta de cloud usada pela aplicação inteira.",
                   "Contagem total de bug reportado no rastreador de issue usado pelo time inteiro.",
                   "Latência de uma única requisição específica, medida em um único momento isolado."],
                  "É o objetivo interno; SLA é o contrato com cliente (geralmente mais conservador).",
                  statement_en="An SLO measures:",
                  correct_en="A service quality objective (e.g., 99.9% availability).",
                  wrong_en=["Total monthly cost charged to the cloud account used by the entire application.",
                            "Total count of bugs reported in the issue tracker used by the whole team.",
                            "The latency of one specific single request, measured at one isolated moment."],
                  explanation_en="It's the internal target; the SLA is the contract with the customer (usually more conservative)."),
                q("Diferença SLI vs SLO:",
                  "SLI é a medida (indicador), SLO é o objetivo.",
                  ["São a mesma coisa, só com nome diferente entre ferramenta.",
                   "O SLO é a métrica bruta coletada direto do sistema monitorado.",
                   "O SLI é o contrato formal assinado diretamente com o cliente."],
                  "Você mede SLI; SLO é o limite que diz se está bom ou ruim.",
                  statement_en="Difference between SLI and SLO:",
                  correct_en="SLI is the measurement (indicator), SLO is the target.",
                  wrong_en=["They're the same thing, just named differently between tools.",
                            "The SLO is the raw metric collected directly from the monitored system.",
                            "The SLI is the formal contract signed directly with the customer."],
                  explanation_en="You measure the SLI; the SLO is the threshold that says whether it's good or bad."),
                q("Por que alarme em SLO em vez de threshold:",
                  "Refletem o que importa para o usuário, não números arbitrários.",
                  ["Substituem completamente a necessidade de manter log estruturado.",
                   "Reduzem o custo mensal pago pela ferramenta de observabilidade.",
                   "Habilitam o protocolo HTTPS na camada de balanceamento de carga."],
                  "Burn rate alerta quando o orçamento de erro está sendo consumido rápido, sinal real, não ruído.",
                  statement_en="Why alert on SLO instead of a raw threshold:",
                  correct_en="They reflect what matters to the user, not arbitrary numbers.",
                  wrong_en=["They completely replace the need to keep structured logs.",
                            "They reduce the monthly cost paid for the observability tool.",
                            "They enable the HTTPS protocol at the load-balancing layer."],
                  explanation_en="A burn rate alert fires when the error budget is being consumed fast, a real signal, not noise."),
                q("PromQL é linguagem de:",
                  "Consulta do Prometheus.",
                  ["JSON, formato de dado usado para troca entre sistema.",
                   "Python usado para escrever a lógica interna de um alarme.",
                   "Formato de log estruturado usado por ferramenta de observabilidade."],
                  "Permite agregações, taxas (`rate(...)[5m]`), percentis (`histogram_quantile`).",
                  statement_en="PromQL is a language for:",
                  correct_en="Querying Prometheus.",
                  wrong_en=["JSON, a data format used for exchange between systems.",
                            "Python used to write the internal logic of an alarm.",
                            "A structured log format used by an observability tool."],
                  explanation_en="Allows aggregations, rates (`rate(...)[5m]`), and percentiles (`histogram_quantile`)."),
                q("Histograma em métricas serve para:",
                  "Distribuir valores em buckets e calcular percentis (p99 etc.).",
                  ["Substituir completamente o uso de trace distribuído na aplicação.",
                   "Contar requisição recebida, sem cálculo estatístico adicional envolvido.",
                   "Listar cada erro individualmente, sem qualquer agregação aplicada ao resultado."],
                  "Histograma é local (cliente). Para somar entre instâncias, use buckets compatíveis.",
                  statement_en="A histogram in metrics is used to:",
                  correct_en="Distribute values into buckets and calculate percentiles (p99, etc.).",
                  wrong_en=["Completely replace the use of distributed tracing in the application.",
                            "Count received requests, with no additional statistical calculation involved.",
                            "List each error individually, with no aggregation applied to the result."],
                  explanation_en="A histogram is local (client-side). To sum across instances, use compatible buckets."),
                q("Alert fadiga ocorre quando:",
                  "Há tantos alertas que ninguém presta atenção.",
                  ["O Prometheus cai e para de coletar métrica nova.",
                   "O SLA contratado aumenta além do que era esperado.",
                   "O Grafana atualiza a versão do dashboard automaticamente."],
                  "Cada alerta sem ação útil corrói a confiança no sistema. Limpe agressivamente.",
                  statement_en="Alert fatigue happens when:",
                  correct_en="So many alerts fire that nobody pays attention.",
                  wrong_en=["Prometheus goes down and stops collecting new metrics.",
                            "The contracted SLA increases beyond what was expected.",
                            "Grafana automatically updates the dashboard's version."],
                  explanation_en="Every alert with no useful action erodes trust in the system. Prune aggressively."),
                q("Métrica vs log vs trace:",
                  "Métrica é numérica agregada; log é evento; trace é fluxo distribuído.",
                  ["São a mesma coisa, só chamada de forma diferente por cada time de engenharia.",
                   "Só o trace importa de verdade, os outros dois são completamente dispensáveis.",
                   "Métrica e trace são exatamente o mesmo conceito, só com nome trocado entre time diferente."],
                  "Os três são pilares da observabilidade, complementares, não substitutos.",
                  statement_en="Metric vs log vs trace:",
                  correct_en="A metric is an aggregated number; a log is an event; a trace is a distributed flow.",
                  wrong_en=["They're the exact same thing, just named differently by each engineering team.",
                            "The trace matters most in practice, the other two are completely dispensable.",
                            "Metric and trace are exactly the same concept, just with the name swapped between different teams."],
                  explanation_en="The three are pillars of observability, complementary, not substitutes."),
                q("SLO de 99,99% permite quantos minutos de downtime/mês?",
                  "Cerca de 4,3 minutos.",
                  ["Cerca de 1 hora inteira de indisponibilidade tolerada por mês.",
                   "0 minutos, já que 99,99% exigiria disponibilidade completa o tempo inteiro.",
                   "Cerca de 1 dia inteiro de indisponibilidade tolerada por mês."],
                  "30d x 24h x 60min x 0,01% ≈ 4,3 min. Quatro noves é caro.",
                  statement_en="How many minutes of downtime/month does a 99.99% SLO allow?",
                  correct_en="About 4.3 minutes.",
                  wrong_en=["About a full hour of downtime tolerated per month.",
                            "0 minutes, since 99.99% would require full uninterrupted availability the whole time.",
                            "About a full day of downtime tolerated per month."],
                  explanation_en="30d x 24h x 60min x 0.01% ≈ 4.3 min. Four nines is expensive."),
                q("Cardinalidade alta em métricas causa:",
                  "Custo crescente e degradação do backend.",
                  ["Auto-resolução do problema sem intervenção humana necessária.",
                   "Backup automático do dado coletado pela ferramenta de métrica.",
                   "Aceleração real da consulta feita contra o banco de métrica."],
                  "Cada combinação única de labels é uma série. Evite user_id/request_id em métricas.",
                  statement_en="High cardinality in metrics causes:",
                  correct_en="Growing cost and backend degradation.",
                  wrong_en=["Automatic resolution of the problem with no human intervention needed.",
                            "Automatic backup of the data collected by the metrics tool.",
                            "A real speedup of the query made against the metrics database."],
                  explanation_en="Every unique combination of labels is a series. Avoid user_id/request_id in metrics."),
            ],
        },
        # =====================================================================
        # 2.9 Backup & DR
        # =====================================================================
        {
            "title": "Backup & Disaster Recovery",
            "title_en": "Backup & Disaster Recovery",
            "summary": "Como não perder tudo em caso de falha.",
            "summary_en": "How not to lose everything when things fail.",
            "lesson": {
                "intro": (
                    "Backup que nunca foi testado não é backup, é otimismo armazenado. "
                    "RTO e RPO são as métricas que separam plano real de ficção corporativa. "
                    "Em 2024, ainda há empresas relevantes que <em>nunca testaram restore "
                    "em produção</em>, e descobrem isso na pior hora possível.<br><br>"
                    "Esta aula cobre: o vocabulário de DR (RPO, RTO, MTBF), a regra 3-2-1 "
                    "modernizada, estratégias de DR (backup-restore até multi-active), "
                    "ransomware-resistant backup, game days, e o caso GitLab 2017 que se "
                    "tornou estudo de caso obrigatório."
                ),
                "intro_en": (
                    "A backup that was never tested isn't a backup, it's stored optimism. "
                    "RTO and RPO are the metrics that separate a real plan from corporate "
                    "fiction. In 2024, there are still relevant companies that <em>never "
                    "tested a restore in production</em>, and find that out at the worst "
                    "possible time.<br><br>"
                    "This lesson covers: the DR vocabulary (RPO, RTO, MTBF), the modernized "
                    "3-2-1 rule, DR strategies (backup-restore all the way to multi-active), "
                    "ransomware-resistant backup, game days, and the GitLab 2017 incident "
                    "that became a mandatory case study."
                ),
                "body": (
                """<h3>1. RPO e RTO, as duas métricas-base</h3>
<p>O <strong>RPO</strong> (Recovery Point Objective) responde "quanto
dado é aceitável perder": se o RPO é de 1 hora, o backup ou a
replicação precisam garantir que o dado esteja, no máximo, uma hora
atrasado em relação ao momento do incidente. O <strong>RTO</strong>
(Recovery Time Objective) responde "em quanto tempo o serviço precisa
voltar": se o RTO é de 30 minutos, qualquer processo manual demorado
já está automaticamente fora de cogitação. Calcular esses dois números
por APLICAÇÃO — não como um valor único para a empresa inteira — é o
que permite escolher a estratégia certa para cada caso, sem pagar por
capacidade de recuperação que uma aplicação de baixo risco nunca vai
precisar:</p>
<div class="mermaid">
flowchart LR
    Backup["Último backup"] -- "RPO: dado que pode se perder" --> Incidente["Incidente"]
    Incidente -- "RTO: tempo até restaurar" --> Restaurado["Serviço restaurado"]
</div>

<table>
<tr><th>App</th><th>RPO</th><th>RTO</th><th>Estratégia</th></tr>
<tr><td>Marketing site (estático)</td><td>24h</td><td>4h</td>
<td>backup &amp; restore</td></tr>
<tr><td>Blog interno</td><td>24h</td><td>8h</td>
<td>backup diário</td></tr>
<tr><td>App SaaS pequena</td><td>1h</td><td>1h</td>
<td>pilot light multi-region</td></tr>
<tr><td>E-commerce</td><td>5min</td><td>30min</td>
<td>warm standby</td></tr>
<tr><td>Trading platform</td><td>0</td><td>&lt;5min</td>
<td>active-active multi-region</td></tr>
</table>

<h3>2. Regra 3-2-1 (e variações modernas)</h3>
<p>A regra clássica de backup pede três cópias do dado (a produção
mais dois backups), guardadas em duas mídias diferentes (não apenas
disco), com pelo menos uma delas offsite — outra região, outra cloud,
outra empresa. A modernização <strong>3-2-1-1-0</strong> acrescenta
mais duas exigências específicas: uma cópia adicional que seja
IMUTÁVEL (via Object Lock ou WORM), e zero erro depois de um teste de
restore real (não presumido). A imutabilidade é resposta direta ao
padrão de ataque moderno de ransomware, onde o atacante ataca o BACKUP
primeiro, sabendo que sem ele a vítima fica sem alternativa a pagar o
resgate — uma cópia que ninguém consegue apagar, nem mesmo o root, até
o prazo de retenção terminar, sobrevive a esse tipo de ataque
especificamente.</p>

<h3>3. Estratégias de DR, quanto custo, quanto tempo</h3>
<table>
<tr><th>Estratégia</th><th>RTO típico</th><th>Custo</th><th>Quando usar</th></tr>
<tr><td>Backup &amp; restore</td><td>horas</td><td>baixo</td>
<td>apps tolerantes a downtime</td></tr>
<tr><td>Pilot light</td><td>30-60min</td><td>baixo-médio</td>
<td>infra mínima ligada na região DR (DB replicando)</td></tr>
<tr><td>Warm standby</td><td>5-30min</td><td>médio-alto</td>
<td>ambiente DR rodando reduzido, escala em caso</td></tr>
<tr><td>Multi-site active-active</td><td>&lt;5min</td><td>2x+</td>
<td>tráfego distribuído entre regiões em produção</td></tr>
</table>
<p>Não existe almoço grátis nessa tabela: cada redução no RTO exige um
aumento correspondente em custo e complexidade operacional. A decisão
certa é escolher a estratégia POR aplicação, de acordo com o RPO/RTO
calculado na seção 1 — não aplicar a mesma estratégia cara a toda a
infraestrutura, nem a mesma estratégia barata onde ela realmente não
serve.</p>

<h3>4. Snapshots ≠ backup</h3>
<p>Um snapshot incremental do EBS é conveniente, mas carrega três
limitações que o desqualificam como backup de verdade sozinho: vive na
MESMA conta, o que significa que uma conta comprometida perde o
snapshot junto com o resto; vive na MESMA região por padrão, o que
significa que uma falha de região inteira o leva junto; e não vem com
object-lock por padrão, deixando aberto para deleção mesmo acidental.
Um backup de verdade precisa ir para outra conta (via cross-account
replication, com IAM totalmente separada), outra região (via
cross-region copy), ou até outro provedor (AWS migrando para Wasabi, ou
um backup local independente) — sempre com retenção imutável
configurada, não apenas presumida.</p>

<h3>5. Ransomware-resistant backup</h3>
<p>O playbook típico de um ataque de ransomware moderno segue uma
sequência bem definida: comprometer credencial via phishing, mapear o
ambiente inteiro (Active Directory, cloud), APAGAR ou criptografar os
backups primeiro (exatamente para eliminar a via de fuga da vítima),
só então criptografar o dado de produção, e finalmente pedir resgate.
Seis defesas em camada quebram essa sequência em pontos diferentes:
Object Lock em modo Compliance impede até o root de apagar; MFA Delete
exige autenticação adicional para deletar qualquer versão; uma conta
totalmente separada garante que a credencial de produção comprometida
não alcança a conta de backup; um air gap lógico mantém o backup num
provedor diferente com credencial independente; um air gap físico —
fita offline, um método antigo mas ainda válido para o tier final de
proteção — fica fisicamente desconectado da rede; e um período de
imutabilidade de 90 dias ou mais dá tempo suficiente para detectar um
comprometimento silencioso antes que ele afete o backup mais recente
também.</p>

<h3>6. Backup de banco de dados, não é só copy</h3>
<p>Um banco transacional exige consistência que uma cópia simples de
arquivo não garante. Um <strong>cold backup</strong> — parar o banco e
copiar o arquivo — é simples mas exige downtime. Um <strong>hot
backup</strong> (<code>pg_basebackup</code> no Postgres,
<code>mysqldump --single-transaction</code> no MySQL) usa um snapshot
de transação para manter consistência mesmo com o banco ativo
recebendo escrita. O <strong>WAL/binlog archiving</strong> habilita PITR
(point-in-time recovery) — um backup base combinado com log contínuo de
transação permite restaurar para qualquer SEGUNDO específico no
passado, não só para o momento do último backup completo. E o
<strong>logical backup</strong> (<code>pg_dump</code>) é mais lento na
execução, mas muito mais portável entre versão diferente do banco ou
schema diferente. O RDS já automatiza tudo isso — backup automático com
retenção configurável, PITR para qualquer segundo dos últimos 35 dias,
snapshot manual sob demanda — mas isso não substitui testar o restore
de verdade (seção 9), só configurar não é suficiente.</p>

<h3>7. Game days, o teste que separa plano de ficção</h3>
<p>Um plano de disaster recovery só vale alguma coisa depois de
efetivamente testado sob condição realista — um game day é exatamente
essa simulação: derrubar a região primária via Fault Injection
Simulator, apagar o banco principal num ambiente isolado e cronometrar
o restore, quebrar DNS, rede ou certificado deliberadamente, com o
engenheiro "de plantão" agindo sem ajuda enquanto o resto do time só
observa e registra. Cinco métricas valem a pena coletar em cada
exercício: tempo até a detecção real do problema, tempo até a decisão
de fazer failover, tempo total de restore, quem precisou ser acordado
fora do horário, e qual documentação estava faltando ou desatualizada
durante a execução. A frequência recomendada é trimestral para
aplicação tier-1 e anual para tier-2 — ferramentas como AWS FIS, Chaos
Mesh, Litmus ou Gremlin automatizam boa parte da injeção de falha
controlada.</p>

<h3>8. Caso real: GitLab 2017, anatomia da limpa</h3>
<p>Em 31 de janeiro de 2017, um engenheiro do GitLab tentando limpar
uma réplica do banco principal rodou por engano <code>rm -rf</code>
direto no BANCO PRINCIPAL, não na réplica — 300 GB de dados apagados
de uma vez. O GitLab tinha cinco mecanismos de backup diferentes
configurados, e na hora de restaurar descobriu que quatro deles não
funcionavam: o backup automático para S3 estava desligado havia meses,
por uma configuração errada que nunca disparou alerta; o snapshot LVM
diário mais recente já tinha 24 horas de idade e levaria 18 horas para
restaurar; o snapshot de disco no Azure nunca chegou a ser ativado; a
replicação para staging estava ativa, mas 6 horas atrasada; e o backup
via <code>pg_dump</code> era literalmente um arquivo de 0 bytes,
quebrado havia tempo sem ninguém perceber. A recuperação final veio do
snapshot LVM, com 6 horas de dado perdido — algumas issues e merge
requests desapareceram para sempre. O GitLab transmitiu o próprio
postmortem ao vivo, um gesto de transparência que virou referência.
As lições documentadas por eles mesmos: de cinco mecanismos de backup,
quatro simplesmente não funcionavam — só testar de verdade revela isso;
"o backup não rodou nas últimas 24h" deveria ser um alerta vermelho
automático, não algo descoberto só na hora da crise; o engenheiro
estava fadigado às 23h quando cometeu o erro, e fadiga é um fator de
incidente real, não só um detalhe anedótico; e um nome de host ambíguo
(db1 versus db2) facilitou diretamente o erro original.</p>

<h3>9. 'Backup is not done until you've tested restore'</h3>
<p>Um ciclo de teste real, rodado mensal ou trimestralmente em
ambiente isolado, segue seis passos: provisionar um recurso novo (banco,
bucket, instância); restaurar o backup mais recente disponível ali;
verificar integridade de verdade — schema correto, contagem de linha
esperada, uma query de smoke test respondendo; cronometrar o tempo
total do processo inteiro; comparar esse tempo medido contra o RTO
documentado (seção 1); e documentar qualquer desvio encontrado, ajustando
o plano de acordo. Automatizar esse ciclo evita que ele dependa de
alguém lembrar de rodá-lo manualmente — o AWS Backup já tem "restore
testing" nativo, e um pipeline em Terraform pode provisionar, restaurar,
validar e destruir tudo automaticamente em sequência.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong>Tratar snapshot na mesma conta como se fosse backup
completo</strong>: não protege contra conta comprometida (seção 4).</li>
<li><strong>Nunca testar o restore</strong>: o erro central que o caso
GitLab (seção 8) tornou público de forma exemplar.</li>
<li><strong>Fazer backup só do banco, esquecendo configuração e
segredo</strong>: restaurar o dado sem a configuração ao redor não
recria o sistema funcional inteiro.</li>
<li><strong>Não criptografar o backup</strong>: se o backup vazar,
vaza tudo que ele contém, sem exceção.</li>
<li><strong>Retenção sem limite superior</strong>: um backup de cinco
anos acumulado sem revisão vira uma das três maiores linhas da fatura,
sem ninguém perceber quando aconteceu.</li>
<li><strong>Sem RTO/RPO documentado por aplicação</strong>: sem esse
número explícito (seção 1), não existe forma objetiva de saber se a
estratégia atual é suficiente.</li>
<li><strong>Plano de DR existe no papel, mas nunca foi executado</strong>:
o mesmo problema da seção 7 — plano não testado é ficção, não
garantia.</li>
<li><strong>Backup guardado numa região vizinha</strong> (us-east-1 e
us-east-2, por exemplo): um desastre geograficamente correlacionado
pode afetar as duas ao mesmo tempo, anulando o propósito de ter
distribuído a cópia.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. RPO and RTO, the two base metrics</h3>
<p>The <strong>RPO</strong> (Recovery Point Objective) answers "how
much data is acceptable to lose": if the RPO is 1 hour, the backup or
replication must guarantee the data is, at most, one hour behind the
moment of the incident. The <strong>RTO</strong> (Recovery Time
Objective) answers "how long can the service take to come back": if
the RTO is 30 minutes, any slow manual process is automatically off
the table. Calculating these two numbers PER APPLICATION — not as a
single value for the entire company — is what lets you choose the
right strategy for each case, without paying for recovery capacity
that a low-risk application will never need:</p>
<div class="mermaid">
flowchart LR
    Backup["Último backup"] -- "RPO: dado que pode se perder" --> Incidente["Incidente"]
    Incidente -- "RTO: tempo até restaurar" --> Restaurado["Serviço restaurado"]
</div>

<table>
<tr><th>App</th><th>RPO</th><th>RTO</th><th>Strategy</th></tr>
<tr><td>Marketing site (static)</td><td>24h</td><td>4h</td>
<td>backup &amp; restore</td></tr>
<tr><td>Internal blog</td><td>24h</td><td>8h</td>
<td>daily backup</td></tr>
<tr><td>Small SaaS app</td><td>1h</td><td>1h</td>
<td>multi-region pilot light</td></tr>
<tr><td>E-commerce</td><td>5min</td><td>30min</td>
<td>warm standby</td></tr>
<tr><td>Trading platform</td><td>0</td><td>&lt;5min</td>
<td>active-active multi-region</td></tr>
</table>

<h3>2. The 3-2-1 rule (and modern variations)</h3>
<p>The classic backup rule calls for three copies of the data
(production plus two backups), stored on two different media (not
just disk), with at least one of them offsite — another region,
another cloud, another company. The <strong>3-2-1-1-0</strong>
modernization adds two more specific requirements: one additional
copy that is IMMUTABLE (via Object Lock or WORM), and zero errors
after a real restore test (not an assumed one). Immutability is a
direct response to the modern ransomware attack pattern, where the
attacker attacks the BACKUP first, knowing that without it the victim
has no alternative but to pay the ransom — a copy nobody can delete,
not even root, until the retention period ends, survives that specific
type of attack.</p>

<h3>3. DR strategies, how much cost, how much time</h3>
<table>
<tr><th>Strategy</th><th>Typical RTO</th><th>Cost</th><th>When to use</th></tr>
<tr><td>Backup &amp; restore</td><td>hours</td><td>low</td>
<td>apps tolerant to downtime</td></tr>
<tr><td>Pilot light</td><td>30-60min</td><td>low-medium</td>
<td>minimal infra running in the DR region (DB replicating)</td></tr>
<tr><td>Warm standby</td><td>5-30min</td><td>medium-high</td>
<td>reduced DR environment running, scales up when needed</td></tr>
<tr><td>Multi-site active-active</td><td>&lt;5min</td><td>2x+</td>
<td>traffic distributed across regions in production</td></tr>
</table>
<p>There's no free lunch in this table: every reduction in RTO
requires a corresponding increase in cost and operational complexity.
The right decision is to choose the strategy PER application,
according to the RPO/RTO calculated in section 1 — not applying the
same expensive strategy to the entire infrastructure, nor the same
cheap strategy where it really doesn't fit.</p>

<h3>4. Snapshots ≠ backup</h3>
<p>An incremental EBS snapshot is convenient, but it carries three
limitations that disqualify it as a real backup on its own: it lives
in the SAME account, meaning a compromised account loses the snapshot
along with everything else; it lives in the SAME region by default,
meaning a full region failure takes it down too; and it doesn't come
with object-lock by default, leaving it open to deletion even
accidentally. A real backup needs to go to another account (via
cross-account replication, with fully separate IAM), another region
(via cross-region copy), or even another provider (AWS migrating to
Wasabi, or an independent local backup) — always with immutable
retention configured, not just assumed.</p>

<h3>5. Ransomware-resistant backup</h3>
<p>The typical playbook of a modern ransomware attack follows a
well-defined sequence: compromise a credential via phishing, map the
entire environment (Active Directory, cloud), DELETE or encrypt the
backups first (precisely to eliminate the victim's escape route), only
then encrypt the production data, and finally demand ransom. Six
layered defenses break that sequence at different points: Object Lock
in Compliance mode prevents even root from deleting; MFA Delete
requires additional authentication to delete any version; a fully
separate account guarantees that a compromised production credential
can't reach the backup account; a logical air gap keeps the backup in
a different provider with an independent credential; a physical air
gap — offline tape, an old but still valid method for the final tier
of protection — stays physically disconnected from the network; and
an immutability period of 90 days or more gives enough time to detect
a silent compromise before it also affects the most recent backup.</p>

<h3>6. Database backup, it's not just copy</h3>
<p>A transactional database requires consistency that a simple file
copy doesn't guarantee. A <strong>cold backup</strong> — stopping the
database and copying the file — is simple but requires downtime. A
<strong>hot backup</strong> (<code>pg_basebackup</code> in Postgres,
<code>mysqldump --single-transaction</code> in MySQL) uses a
transaction snapshot to maintain consistency even with the database
actively receiving writes. <strong>WAL/binlog archiving</strong>
enables PITR (point-in-time recovery) — a base backup combined with
continuous transaction logging lets you restore to any specific
SECOND in the past, not just to the moment of the last full backup.
And a <strong>logical backup</strong> (<code>pg_dump</code>) is slower
to run, but much more portable between different database versions or
schemas. RDS already automates all of this — automatic backup with
configurable retention, PITR for any second in the last 35 days,
on-demand manual snapshot — but that doesn't replace actually testing
the restore (section 9), configuring it alone isn't enough.</p>

<h3>7. Game days, the test that separates plan from fiction</h3>
<p>A disaster recovery plan is only worth something after being
actually tested under realistic conditions — a game day is exactly
that simulation: taking down the primary region via Fault Injection
Simulator, deleting the main database in an isolated environment and
timing the restore, deliberately breaking DNS, network, or
certificate, with the "on-call" engineer acting without help while the
rest of the team only observes and records. Five metrics are worth
collecting in each exercise: time to actual detection of the problem,
time to the decision to fail over, total restore time, who needed to
be woken up off-hours, and what documentation was missing or outdated
during execution. The recommended frequency is quarterly for tier-1
applications and yearly for tier-2 — tools like AWS FIS, Chaos Mesh,
Litmus, or Gremlin automate a good part of the controlled failure
injection.</p>

<h3>8. Real case: GitLab 2017, anatomy of the wipe</h3>
<p>On January 31, 2017, a GitLab engineer trying to clean up a replica
of the main database mistakenly ran <code>rm -rf</code> directly on
the MAIN database, not the replica — 300 GB of data deleted at once.
GitLab had five different backup mechanisms configured, and when it
came time to restore they discovered four of them didn't work: the
automatic backup to S3 had been off for months, due to a
misconfiguration that never triggered an alert; the most recent daily
LVM snapshot was already 24 hours old and would take 18 hours to
restore; the Azure disk snapshot had never actually been enabled; the
replication to staging was active, but 6 hours behind; and the
<code>pg_dump</code> backup was literally a 0-byte file, broken for a
long time without anyone noticing. The final recovery came from the
LVM snapshot, with 6 hours of data lost — some issues and merge
requests disappeared forever. GitLab live-streamed its own postmortem,
a transparency move that became a reference. The lessons they
documented themselves: out of five backup mechanisms, four simply
didn't work — only real testing reveals that; "the backup hasn't run
in the last 24h" should be an automatic red-flag alert, not something
discovered only during the crisis; the engineer was fatigued at 11pm
when he made the mistake, and fatigue is a real incident factor, not
just an anecdotal detail; and an ambiguous hostname (db1 versus db2)
directly contributed to the original error.</p>

<h3>9. 'Backup is not done until you've tested restore'</h3>
<p>A real test cycle, run monthly or quarterly in an isolated
environment, follows six steps: provision a new resource (database,
bucket, instance); restore the most recent available backup onto it;
verify integrity for real — correct schema, expected row count, a
smoke-test query responding; time the entire process; compare that
measured time against the documented RTO (section 1); and document any
deviation found, adjusting the plan accordingly. Automating this cycle
prevents it from depending on someone remembering to run it manually —
AWS Backup already has native "restore testing", and a Terraform
pipeline can provision, restore, validate, and destroy everything
automatically in sequence.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong>Treating a same-account snapshot as if it were a
complete backup</strong>: doesn't protect against a compromised
account (section 4).</li>
<li><strong>Never testing the restore</strong>: the central mistake
that the GitLab case (section 8) made public in exemplary fashion.</li>
<li><strong>Backing up only the database, forgetting configuration
and secrets</strong>: restoring the data without the surrounding
configuration doesn't recreate the whole functional system.</li>
<li><strong>Not encrypting the backup</strong>: if the backup leaks,
everything it contains leaks, without exception.</li>
<li><strong>Retention with no upper bound</strong>: five years of
accumulated backups with no review becomes one of the top three lines
on the bill, without anyone noticing when it happened.</li>
<li><strong>No RTO/RPO documented per application</strong>: without
that explicit number (section 1), there's no objective way to know if
the current strategy is enough.</li>
<li><strong>DR plan exists on paper, but was never executed</strong>:
the same problem from section 7 — an untested plan is fiction, not a
guarantee.</li>
<li><strong>Backup stored in a neighboring region</strong> (us-east-1
and us-east-2, for example): a geographically correlated disaster can
affect both at the same time, negating the purpose of having
distributed the copy.</li>
</ul>"""
                ),
                "practical": (
                    "(1) Faça snapshot/backup do seu banco de teste (RDS, Postgres, MySQL "
                    "qualquer).<br>"
                    "(2) <strong>Apague o banco</strong>. (Em ambiente de teste! Não em "
                    "prod!)<br>"
                    "(3) Provisione novo banco na <em>outra região</em>.<br>"
                    "(4) Restaure do backup. Cronometre <strong>do passo 2 ao último query "
                    "respondendo</strong>.<br>"
                    "(5) Compare com o RTO que você assumia. Provavelmente vai surpreender "
                    "para cima.<br>"
                    "(6) Bônus: configure object-lock de 30d em um bucket S3, faça upload, "
                    "tente apagar, veja a denial.<br>"
                    "(7) Bônus 2: agende game day mensal calendário do time para repetir "
                    "esse exercício."
                ),
                "practical_en": (
                    "(1) Take a snapshot/backup of your test database (RDS, Postgres, MySQL, "
                    "any).<br>"
                    "(2) <strong>Delete the database</strong>. (In a test environment! Not in "
                    "prod!)<br>"
                    "(3) Provision a new database in the <em>other region</em>.<br>"
                    "(4) Restore from the backup. Time it <strong>from step 2 to the last "
                    "query responding</strong>.<br>"
                    "(5) Compare with the RTO you assumed. It will probably surprise you, on "
                    "the wrong side.<br>"
                    "(6) Bonus: configure 30-day object-lock on an S3 bucket, upload a file, "
                    "try to delete it, watch the denial.<br>"
                    "(7) Bonus 2: schedule a monthly game day on the team calendar to repeat "
                    "this exercise."
                ),
            },
            "materials": [
                m("AWS Backup",
                  "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html",
                  "docs", "", title_en="AWS Backup", description_en=""),
                m("Veeam: 3-2-1 backup rule",
                  "https://www.veeam.com/blog/321-backup-rule.html", "article", "",
                  title_en="Veeam: 3-2-1 backup rule", description_en=""),
                m("Google: Disaster Recovery Planning",
                  "https://cloud.google.com/architecture/dr-scenarios-planning-guide",
                  "article", "", title_en="Google: Disaster Recovery Planning",
                  description_en=""),
                m("Azure Site Recovery",
                  "https://learn.microsoft.com/azure/site-recovery/site-recovery-overview",
                  "docs", "", title_en="Azure Site Recovery", description_en=""),
                m("Restic backup", "https://restic.readthedocs.io/", "tool",
                  "Open source, deduplicado, criptografado.",
                  title_en="Restic backup", description_en="Open source, deduplicated, encrypted."),
                m("AWS Fault Injection Simulator",
                  "https://docs.aws.amazon.com/fis/latest/userguide/what-is.html",
                  "tool", "Game day on demand.",
                  title_en="AWS Fault Injection Simulator",
                  description_en="Game day on demand."),
            ],
            "questions": [
                q("RPO mede:",
                  "Quanto dado é aceitável perder em caso de incidente.",
                  ["O tempo necessário até o serviço voltar a funcionar por completo.",
                   "O custo mensal cobrado pela conta de cloud utilizada.",
                   "A velocidade de leitura e escrita do disco usado no servidor."],
                  "RPO baixo = backups frequentes. RPO=0 só com replicação síncrona, e cara.",
                  statement_en="RPO measures:",
                  correct_en="How much data is acceptable to lose in an incident.",
                  wrong_en=["How long it takes for the service to fully come back online.",
                            "The monthly cost charged by the cloud account in use.",
                            "The read/write speed of the disk used on the server."],
                  explanation_en="Low RPO = frequent backups. RPO=0 only with synchronous replication, and it's expensive."),
                q("RTO mede:",
                  "Tempo aceitável para retomar a operação.",
                  ["A latência de rede medida entre cliente e servidor.",
                   "O throughput máximo suportado pela aplicação em produção.",
                   "A quantidade de dado perdido em caso de falha grave."],
                  "RTO baixo = automação. Atender RTO de minutos manualmente é impossível.",
                  statement_en="RTO measures:",
                  correct_en="The acceptable time to resume operation.",
                  wrong_en=["The network latency measured between client and server.",
                            "The maximum throughput the application supports in production.",
                            "The amount of data lost in a severe failure."],
                  explanation_en="Low RTO = automation. Meeting an RTO of minutes manually is impossible."),
                q("Regra 3-2-1 sugere:",
                  "3 cópias, em 2 mídias, com 1 offsite.",
                  ["3 réplica guardada no mesmo disco físico, sem separação real.",
                   "Fazer backup uma vez por semana, sem cópia adicional.",
                   "Uma cópia local guardada só na própria máquina de produção."],
                  "Sobrevive a incêndio do datacenter, ransomware na conta principal e mídia falha.",
                  statement_en="The 3-2-1 rule suggests:",
                  correct_en="3 copies, on 2 media, with 1 offsite.",
                  wrong_en=["3 replicas stored on the same physical disk, with no real separation.",
                            "Backing up once a week, with no additional copy.",
                            "One local copy stored only on the production machine itself."],
                  explanation_en="Survives a datacenter fire, ransomware on the main account, and media failure."),
                q("Snapshot incremental:",
                  "Salva só as mudanças desde o último snapshot.",
                  ["Salva o conteúdo inteiro de novo a cada execução do processo.",
                   "Substitui completamente o backup full mais recente disponível.",
                   "Apaga o snapshot mais antigo automaticamente após cada execução."],
                  "Eficiente em espaço, mas restore depende da cadeia de incrementais.",
                  statement_en="Incremental snapshot:",
                  correct_en="Saves only the changes since the last snapshot.",
                  wrong_en=["Saves the entire content again on every run of the process.",
                            "Completely replaces the most recent full backup available.",
                            "Automatically deletes the oldest snapshot after every run."],
                  explanation_en="Space-efficient, but restore depends on the chain of incrementals."),
                q("Backup sem teste é:",
                  "Inútil, só descobre o problema na hora.",
                  ["Rápido de restaurar na maioria dos casos, independente do tamanho.",
                   "Uma garantia legal válida perante qualquer auditoria externa.",
                   "Suficiente para cumprir a exigência de compliance da empresa."],
                  "Game day mensal/trimestral revela schemas que mudaram, credenciais que expiraram, etc.",
                  statement_en="A backup without testing is:",
                  correct_en="Useless, you only find the problem when it's too late.",
                  wrong_en=["Fast to restore in most cases, regardless of size or backup type.",
                            "A valid legal guarantee against any external audit.",
                            "Enough to meet the company's compliance requirement."],
                  explanation_en="Monthly/quarterly game days reveal changed schemas, expired credentials, etc."),
                q("DR em região alternativa serve para:",
                  "Mitigar falha de uma região inteira.",
                  ["Aumentar o custo mensal pago pela infraestrutura de backup.",
                   "Trocar de provedor de cloud durante a migração de dado.",
                   "Reduzir a latência local da aplicação para o usuário final."],
                  "Region failures são raros mas existem (us-east-1 outages).",
                  statement_en="DR in an alternate region serves to:",
                  correct_en="Mitigate the failure of an entire region.",
                  wrong_en=["Increase the monthly cost paid for backup infrastructure.",
                            "Switch cloud providers during a data migration.",
                            "Reduce local latency for the application's end user."],
                  explanation_en="Region failures are rare but they do happen (us-east-1 outages)."),
                q("Encriptação de backup é:",
                  "Obrigatória, backup vaza, dado vaza.",
                  ["Só necessária quando o backup contém dado de banco de dados.",
                   "Opcional, dependendo da política interna definida pela equipe.",
                   "Inútil, porque o backup já fica protegido pelo isolamento de rede."],
                  "Backup é onde quase todo dado está, junto. KMS + bucket policy restritiva.",
                  statement_en="Encrypting a backup is:",
                  correct_en="Mandatory, if the backup leaks, the data leaks.",
                  wrong_en=["Only necessary when the backup contains database data.",
                            "Optional, depending on the team's internal policy.",
                            "Useless, because the backup is already protected by network isolation."],
                  explanation_en="Backup is where almost all the data sits, together. KMS plus a restrictive bucket policy."),
                q("Game day em DR é:",
                  "Simulação real para validar runbooks.",
                  ["Uma festa de confraternização organizada pelo time de infra.",
                   "Um hackathon interno para testar ideia nova de produto.",
                   "Uma auditoria fiscal conduzida por contador externo contratado."],
                  "Documente lições aprendidas e ajuste runbook após cada game day.",
                  statement_en="A game day in DR is:",
                  correct_en="A real simulation to validate runbooks.",
                  wrong_en=["A team party organized by the infrastructure team.",
                            "An internal hackathon to test a new product idea.",
                            "A tax audit conducted by an outside contracted accountant."],
                  explanation_en="Document lessons learned and adjust the runbook after each game day."),
                q("Pilot light é:",
                  "Estratégia DR com infraestrutura mínima ativa em outra região.",
                  ["Um modo específico de configuração dentro do IAM da conta.",
                   "Uma tarefa agendada (cron) rodando periodicamente no servidor.",
                   "Um tipo específico de classe de armazenamento dentro do S3."],
                  "Equilibra custo (baixo) com RTO razoável (minutos), comparado a backup-restore (horas).",
                  statement_en="Pilot light is:",
                  correct_en="A DR strategy with minimal infrastructure active in another region.",
                  wrong_en=["A specific configuration mode inside the account's IAM.",
                            "A scheduled task (cron) running periodically on the server to clean up temp files.",
                            "A specific storage class type inside S3."],
                  explanation_en="Balances cost (low) with a reasonable RTO (minutes), compared to backup-restore (hours)."),
                q("Cold backup vs hot backup:",
                  "Cold é com app parado; hot é com app rodando (consistente).",
                  ["O hot backup é mais simples de configurar do que o cold.",
                   "Os dois são idênticos, sem diferença prática relevante entre eles.",
                   "O cold backup fica disponível online durante o processo inteiro de cópia."],
                  "Hot exige consistência transacional (ex.: snapshot WAL do Postgres).",
                  statement_en="Cold backup vs hot backup:",
                  correct_en="Cold means the app is stopped; hot means the app keeps running (consistent).",
                  wrong_en=["Hot backup is simpler to configure than cold backup.",
                            "The two are completely identical, with no relevant practical difference between them at all.",
                            "Cold backup stays online for the entire duration of the copy process."],
                  explanation_en="Hot requires transactional consistency (e.g., Postgres WAL snapshot)."),
            ],
        },
        # =====================================================================
        # 2.10 FinOps
        # =====================================================================
        {
            "title": "FinOps Inicial",
            "title_en": "FinOps Fundamentals",
            "summary": "Evitar surpresas na fatura do cartão de crédito no fim do mês.",
            "summary_en": "Avoiding surprises on the credit card bill at the end of the month.",
            "lesson": {
                "intro": (
                    "Cloud cobra por consumo. Sem disciplina, o orçamento vira surpresa de "
                    "fim de mês, uma startup deu manchete em 2021 com fatura de US$ 14k "
                    "depois de um bug em loop. Em escala maior, é comum ver empresas com "
                    "faturas de US$ 1M+ onde 30-40% é desperdício.<br><br>"
                    "FinOps é a prática de unir engenharia + finanças + produto para "
                    "decidir bem com base em dados de custo. Esta aula cobre os fundamentos: "
                    "tagging, modelos de cobrança, right-sizing, recursos órfãos, "
                    "auto-scaling, e cultura, sem ela, a melhor ferramenta vira shelfware."
                ),
                "intro_en": (
                    "Cloud charges by consumption. Without discipline, the budget turns into "
                    "an end-of-month surprise, a startup made headlines in 2021 with a $14k "
                    "bill after a bug caused a loop. At larger scale, it's common to see "
                    "companies with $1M+ bills where 30-40% is waste.<br><br>"
                    "FinOps is the practice of bringing engineering + finance + product "
                    "together to make good decisions based on cost data. This lesson covers "
                    "the fundamentals: tagging, billing models, right-sizing, orphaned "
                    "resources, auto-scaling, and culture, without which the best tool turns "
                    "into shelfware."
                ),
                "body": (
                """<h3>1. Por que FinOps existe</h3>
<p>Em ambiente on-prem, comprar hardware era uma decisão de comitê:
seis meses de discussão, capex aprovado em orçamento, contrato
assinado — cada decisão de custo passava por um filtro pesado antes de
acontecer. Em cloud, qualquer desenvolvedor provisiona uma EC2 com um
único clique. A velocidade aumenta muito, mas a decisão de custo se
distribui de repente para centenas de pessoas diferentes, sem o mesmo
filtro. Sem um framework para acompanhar isso, o resultado inverte: em
vez de poucas decisões grandes e bem pensadas, surgem muitas decisões
pequenas e mal calculadas somando uma fatura mensal absurda no fim. O
ponto central do FinOps não é cortar custo por cortar — às vezes a
decisão certa é gastar MAIS, escalando de propósito para atender um
pico previsto como Black Friday. O que FinOps garante é decisão
CONSCIENTE, tomada com dado de custo real na mesa, não decisão no
escuro.</p>
<div class="mermaid">
flowchart LR
    A["Provisiona recurso"] --> B["Custo gerado"]
    B --> C["Visibilidade: tag e dashboard"]
    C --> D{"Recurso subutilizado?"}
    D -- "Sim" --> E["Redimensiona ou desliga"]
    D -- "Não" --> A
    E --> A
</div>


<h3>2. Visibilidade primeiro: tagging strategy</h3>
<p>Sem tag, você sabe que está pagando US$ 50 mil por mês, mas não tem
como saber QUEM está usando esse valor. O padrão recomendado define um
conjunto de tags obrigatórias para todo recurso criado:</p>
<table>
<tr><th>Tag</th><th>Exemplo</th><th>Para quê</th></tr>
<tr><td><code>Environment</code></td><td>prod, staging, dev</td>
<td>separar custo por ambiente</td></tr>
<tr><td><code>Owner</code></td><td>team-payments@</td>
<td>quem responde se algo sumir</td></tr>
<tr><td><code>CostCenter</code></td><td>CC-1234</td>
<td>chargeback contábil</td></tr>
<tr><td><code>Project</code></td><td>checkout-redesign</td>
<td>ROI por projeto</td></tr>
<tr><td><code>ManagedBy</code></td><td>terraform, manual</td>
<td>identificar drift</td></tr>
<tr><td><code>ExpiresAt</code></td><td>2026-12-31</td>
<td>recursos temporários</td></tr>
</table>
<p>Impor isso via SCP ou Org Policy — negando a criação de qualquer
recurso sem a tag obrigatória presente — transforma a exigência de
convenção seguida por boa vontade em regra estruturalmente aplicada. E
ativar cost allocation tags no AWS Billing é o passo que finalmente
torna essas tags filtráveis dentro do Cost Explorer, fechando o ciclo
entre "marcar o recurso" e "conseguir ver o custo por tag" de verdade.</p>

<h3>3. Modelos de cobrança em AWS (e equivalentes)</h3>
<table>
<tr><th>Modelo</th><th>Desconto</th><th>Compromisso</th><th>Quando</th></tr>
<tr><td>On-demand</td><td>0%</td><td>nenhum</td>
<td>desenvolvimento, picos imprevisíveis</td></tr>
<tr><td>Reserved Instance (1y)</td><td>até 40%</td><td>1 ano, type fixo</td>
<td>baseline previsível</td></tr>
<tr><td>Reserved Instance (3y)</td><td>até 60%</td><td>3 anos, type fixo</td>
<td>workload core estável</td></tr>
<tr><td>Savings Plans</td><td>até 70%</td>
<td>1-3 anos, US$/h flexível em type/region</td>
<td>baseline mas com flexibilidade</td></tr>
<tr><td>Spot Instance</td><td>até 90%</td>
<td>nenhum, pode ser interrompida com 2min de aviso</td>
<td>batch, CI, ML training, workload tolerante</td></tr>
</table>
<p>Uma estratégia típica em produção madura combina os três: cerca de
70% da carga baseline em Savings Plans (cobrindo compute, Lambda e
Fargate), cerca de 20% em Spot para workload tolerante a interrupção, e
apenas 10% em on-demand reservado para pico realmente imprevisível — o
compromisso de longo prazo cobre o que é previsível, e o restante fica
flexível.</p>

<h3>4. Right-sizing, a maioria das instâncias está superprovisionada</h3>
<p>Uma análise típica em ambiente maduro encontra 30% a 50% das
instâncias EC2 com CPU médio sustentado abaixo de 10% — a empresa está
pagando integralmente por capacidade que raramente usa de fato. AWS
Compute Optimizer, Azure Advisor e GCP Recommender fazem esse
diagnóstico automaticamente, analisando a métrica real do CloudWatch (ou
equivalente) e sugerindo instância menor. Quatro estratégias resolvem
o problema uma vez identificado: trocar de família — de
<code>m6i</code> (uso geral) para <code>t3</code> (burst) numa
aplicação com tráfego bem variável; reduzir o tamanho diretamente —
<code>m6i.2xlarge</code> para <code>m6i.large</code> quando a CPU média
fica abaixo de 30%; migrar para Graviton (ARM) — mesmo desempenho por
cerca de 20% menos custo, usando famílias <code>m6g</code>,
<code>c7g</code>, seja recompilando para ARM ou usando uma imagem
multi-arch já pronta; e, para carga muito variável, migrar para
serverless (Lambda, Fargate, Cloud Run), que escala até zero quando
ninguém está usando.</p>

<h3>5. Recursos órfãos, o ralo silencioso</h3>
<p>Em qualquer conta com mais de seis meses de uso, um conjunto
previsível de recurso esquecido se acumula: volume EBS desanexado
depois que a instância original foi apagada; snapshot de anos atrás
sem ninguém revisar; Elastic IP não associado, cobrando US$ 0,005 por
hora mesmo parado; NAT Gateway esquecido numa VPC que não recebe mais
tráfego nenhum; RDS em estado <code>stopped</code>, que continua
cobrando storage mesmo parado; bucket S3 com data lake gigante de uma
prova de conceito abandonada; log do CloudWatch sem retenção
configurada, crescendo indefinidamente; load balancer sem nenhum target
atrás dele; e função Lambda com retenção de log infinita. Em ambiente
grande, isso soma de 5% a 15% da fatura inteira, silenciosamente. Uma
auditoria automatizada com Cloud Custodian resolve isso de forma
estruturada:</p>
<pre><code># custodian.yml
policies:
  - name: ebs-unattached-old
    resource: ebs
    filters:
      - State: available           # desanexado
      - type: value
        key: CreateTime
        op: less-than
        value_type: age
        value: 30
    actions:
      - type: tag
        tags:
          'cleanup': 'pending'
      - type: notify
        to: ['platform@example.com']</code></pre>
<p>Após o dono do recurso revisar a marcação, uma segunda passada faz
a deleção de fato — nunca automática de primeira, para evitar apagar
algo que na verdade ainda estava em uso legítimo.</p>

<h3>6. Auto-scaling como FinOps</h3>
<p>Provisionar capacidade fixa para o pico esperado significa pagar
pelo pico o tempo INTEIRO, mesmo nas horas de tráfego baixo — o
auto-scaling resolve isso ajustando capacidade dinamicamente conforme
demanda real. O EC2 Auto Scaling Group faz target tracking (manter CPU
média em, digamos, 60%). O HPA do Kubernetes (Horizontal Pod
Autoscaler) escala pod com base em métrica customizada. O Cluster
Autoscaler ou o Karpenter no Kubernetes adiciona ou remove NODE
inteiro conforme pod pendente aparece ou desaparece. O Lambda escala
até zero quando ninguém está chamando a função. E o Fargate cobra
apenas pelo container efetivamente rodando, escalando de zero até N
sem gerenciar nenhum servidor por trás. O Karpenter merece destaque
específico: ele provisiona o node exato para o pod que precisa dele —
escolhendo Spot quando possível e a família/tamanho certos para aquela
carga específica — entregando uma economia substancial comparado ao
Cluster Autoscaler clássico, que trabalha com grupo de instância mais
genérico.</p>

<h3>7. Egress, NAT Gateway, e os custos invisíveis</h3>
<table>
<tr><th>Item</th><th>$/unidade</th><th>Estimativa de impacto</th></tr>
<tr><td>Tráfego saindo da AWS</td><td>~$0.09/GB</td>
<td>app que serve vídeo: $$$</td></tr>
<tr><td>Tráfego cross-region</td><td>~$0.02/GB</td>
<td>replicação descuidada</td></tr>
<tr><td>Tráfego cross-AZ</td><td>~$0.01/GB</td>
<td>app em K8s sem topology aware routing</td></tr>
<tr><td>NAT Gateway</td><td>~$32/mês + $0.045/GB</td>
<td>privada → internet caro</td></tr>
<tr><td>VPC Endpoint Interface</td><td>~$7/mês por AZ</td>
<td>caro em escala mas pode valer</td></tr>
</table>
<p>Cinco mitigações reduzem essa categoria de custo silencioso: VPC
Endpoint Gateway para S3 e DynamoDB (gratuito, e já detalhado na aula
de VPC); CloudFront cobrando um preço por GB mais baixo do que egress
direto; compressão HTTP (gzip, brotli) reduzindo o volume real
transferido; cache na borda evitando repetir a mesma transferência
várias vezes; e roteamento topology-aware no Kubernetes, priorizando
tráfego dentro da mesma AZ antes de cruzar para outra.</p>

<h3>8. Budgets, alertas e quotas</h3>
<p>Configurar isso ANTES do primeiro deploy — não depois do primeiro
susto — é o que separa uma fatura administrada de uma surpresa de fim
de mês:</p>
<pre><code>resource "aws_budgets_budget" "monthly" {
  name         = "prod-monthly"
  budget_type  = "COST"
  limit_amount = "5000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  
  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 50
    threshold_type      = "PERCENTAGE"
    notification_type   = "FORECASTED"
    subscriber_email_addresses = ["finance@example.com"]
  }
  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 90
    notification_type   = "ACTUAL"
    subscriber_email_addresses = ["oncall@example.com"]
  }
}</code></pre>
<p>Numa conta de sandbox especificamente, vale considerar o AWS Budget
Action — aplicando uma SCP que nega <code>RunInstances</code>
automaticamente ao atingir 100% do orçamento configurado, evitando que
um bug em loop (como o caso do jornalista holandês da aula anterior)
tenha chance de explodir sem nenhum limite prático.</p>

<h3>9. Cultura FinOps: Crawl / Walk / Run</h3>
<p>A FinOps Foundation define três estágios progressivos de
maturidade, e pular etapa é o erro mais comum. No estágio
<strong>Crawl</strong>, o foco é visibilidade básica: tag, Cost
Explorer, budget configurado, KPI simples acompanhado. No
<strong>Walk</strong>, entra a otimização contínua: right-sizing
automatizado, showback por equipe (cada time vendo o próprio custo), e
detecção de anomalia de custo. No <strong>Run</strong>, a decisão de
PRODUTO já é diretamente influenciada por custo: chargeback real entre
áreas, forecasting integrado ao planejamento, e unit economics
calculada por transação (<code>$ / transação</code>). Sem a
visibilidade básica do Crawl bem estabelecida primeiro, qualquer
tentativa de "otimização" no estágio seguinte acaba baseada em dado
distorcido ou incompleto.</p>

<h3>10. Caso real: Fly.io e a fatura inesperada</h3>
<p>Em 2024, a Fly.io publicou um postmortem público sobre um cliente
cuja VM entrou em crash loop, gerando 50 TB de transferência
cross-region em apenas dois dias — uma fatura projetada de US$ 70 mil.
As lições documentadas do incidente: o cliente tinha um budget
configurado, mas nunca chegou a configurar o ALERTA correspondente,
tornando o budget inútil na prática; o loop levou 18 horas até ser
detectado pelo próprio time; a Fly.io absorveu 80% do custo como
gesto de boa relação com o cliente; a lição que a Fly.io tirou foi
aplicar rate-limit de egress por padrão em conta nova, prevenindo o
mesmo cenário estrutural; e a lição do lado do cliente foi configurar
alerta especificamente em "tráfego por minuto acima de X" — o tipo de
sinal que teria detectado o problema em minutos, não em horas.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Comprar Reserved de 3 anos sem analisar padrão de
uso</strong>: trava um compromisso longo sobre uma suposição não
verificada.</li>
<li><strong>Não usar tag, todo recurso vira "misc"</strong>: elimina a
visibilidade que sustenta qualquer decisão informada (seção 2).</li>
<li><strong>Sem retenção configurada no CloudWatch Logs</strong>:
cresce indefinidamente sem limite, um dos órfãos mais comuns (seção
5).</li>
<li><strong>Snapshot diário de tudo sem expiração</strong>: acumula
custo de storage sem nenhum limite de retenção real.</li>
<li><strong>Provisionar instância grande "para garantir" sem
medir</strong>: exatamente o padrão que o right-sizing (seção 4) existe
para corrigir.</li>
<li><strong>Spot em workload stateful sem checkpoint</strong>: perde
progresso inteiro a cada interrupção de 2 minutos de aviso.</li>
<li><strong>Sem alerta de anomalia configurado</strong>: o Cost
Anomaly Detection é gratuito na AWS e raramente é ativado mesmo
assim.</li>
<li><strong>Time financeiro sem acesso ao Cost Explorer</strong>: quem
mais precisaria do dado de custo fica sem o acesso direto a ele.</li>
<li><strong>Showback que ninguém olha</strong>: gerar o relatório não
basta se ele não influencia decisão real de nenhum time.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Why FinOps exists</h3>
<p>In an on-prem environment, buying hardware was a committee
decision: six months of discussion, capex approved in a budget,
contract signed — every cost decision went through a heavy filter
before happening. In the cloud, any developer provisions an EC2
instance with a single click. Speed increases a lot, but the cost
decision suddenly spreads to hundreds of different people, without the
same filter. Without a framework to track this, the outcome inverts:
instead of a few large, well-thought-out decisions, many small,
poorly-calculated decisions pile up into an absurd monthly bill in the
end. The central point of FinOps isn't cutting cost for cutting's
sake — sometimes the right decision is to spend MORE, scaling on
purpose to handle an expected spike like Black Friday. What FinOps
guarantees is a CONSCIOUS decision, made with real cost data on the
table, not a decision made in the dark.</p>
<div class="mermaid">
flowchart LR
    A["Provisiona recurso"] --> B["Custo gerado"]
    B --> C["Visibilidade: tag e dashboard"]
    C --> D{"Recurso subutilizado?"}
    D -- "Sim" --> E["Redimensiona ou desliga"]
    D -- "Não" --> A
    E --> A
</div>


<h3>2. Visibility first: tagging strategy</h3>
<p>Without tags, you know you're paying $50 thousand a month, but you
have no way to know WHO is using that amount. The recommended standard
defines a set of mandatory tags for every resource created:</p>
<table>
<tr><th>Tag</th><th>Example</th><th>What it's for</th></tr>
<tr><td><code>Environment</code></td><td>prod, staging, dev</td>
<td>separate cost by environment</td></tr>
<tr><td><code>Owner</code></td><td>team-payments@</td>
<td>who's accountable if something disappears</td></tr>
<tr><td><code>CostCenter</code></td><td>CC-1234</td>
<td>accounting chargeback</td></tr>
<tr><td><code>Project</code></td><td>checkout-redesign</td>
<td>ROI per project</td></tr>
<tr><td><code>ManagedBy</code></td><td>terraform, manual</td>
<td>identify drift</td></tr>
<tr><td><code>ExpiresAt</code></td><td>2026-12-31</td>
<td>temporary resources</td></tr>
</table>
<p>Enforcing this via SCP or Org Policy — denying the creation of any
resource without the mandatory tag present — turns the requirement
from a convention followed by good will into a structurally enforced
rule. And enabling cost allocation tags in AWS Billing is the step
that finally makes those tags filterable inside Cost Explorer, closing
the loop between "tagging the resource" and actually "being able to
see the cost by tag".</p>

<h3>3. Billing models in AWS (and equivalents)</h3>
<table>
<tr><th>Model</th><th>Discount</th><th>Commitment</th><th>When</th></tr>
<tr><td>On-demand</td><td>0%</td><td>none</td>
<td>development, unpredictable spikes</td></tr>
<tr><td>Reserved Instance (1y)</td><td>up to 40%</td><td>1 year, fixed type</td>
<td>predictable baseline</td></tr>
<tr><td>Reserved Instance (3y)</td><td>up to 60%</td><td>3 years, fixed type</td>
<td>stable core workload</td></tr>
<tr><td>Savings Plans</td><td>up to 70%</td>
<td>1-3 years, flexible $/h across type/region</td>
<td>baseline but with flexibility</td></tr>
<tr><td>Spot Instance</td><td>up to 90%</td>
<td>none, can be interrupted with 2min notice</td>
<td>batch, CI, ML training, tolerant workload</td></tr>
</table>
<p>A typical strategy in mature production combines all three: about
70% of the baseline load on Savings Plans (covering compute, Lambda,
and Fargate), about 20% on Spot for interruption-tolerant workloads,
and only 10% reserved on-demand for truly unpredictable spikes — the
long-term commitment covers what's predictable, and the rest stays
flexible.</p>

<h3>4. Right-sizing, most instances are overprovisioned</h3>
<p>A typical analysis in a mature environment finds 30% to 50% of EC2
instances with sustained average CPU below 10% — the company is paying
in full for capacity it rarely actually uses. AWS Compute Optimizer,
Azure Advisor, and GCP Recommender make this diagnosis automatically,
analyzing real CloudWatch metrics (or equivalent) and suggesting a
smaller instance. Four strategies solve the problem once identified:
switching family — from <code>m6i</code> (general purpose) to
<code>t3</code> (burstable) for an application with highly variable
traffic; reducing the size directly — <code>m6i.2xlarge</code> to
<code>m6i.large</code> when average CPU stays below 30%; migrating to
Graviton (ARM) — the same performance for about 20% less cost, using
the <code>m6g</code>, <code>c7g</code> families, either recompiling
for ARM or using an already-ready multi-arch image; and, for highly
variable load, migrating to serverless (Lambda, Fargate, Cloud Run),
which scales to zero when nobody's using it.</p>

<h3>5. Orphaned resources, the silent drain</h3>
<p>In any account with more than six months of use, a predictable set
of forgotten resources accumulates: an EBS volume detached after the
original instance was deleted; a snapshot from years ago that nobody
reviews; an unassociated Elastic IP, charging $0.005 per hour even
while idle; a NAT Gateway forgotten in a VPC that no longer receives
any traffic; an RDS instance in <code>stopped</code> state, which keeps
charging for storage even while stopped; an S3 bucket with a giant
data lake from an abandoned proof of concept; a CloudWatch log with no
retention configured, growing indefinitely; a load balancer with no
target behind it; and a Lambda function with infinite log retention.
In a large environment, this adds up to 5% to 15% of the entire bill,
silently. An automated audit with Cloud Custodian resolves this in a
structured way:</p>
<pre><code># custodian.yml
policies:
  - name: ebs-unattached-old
    resource: ebs
    filters:
      - State: available           # desanexado
      - type: value
        key: CreateTime
        op: less-than
        value_type: age
        value: 30
    actions:
      - type: tag
        tags:
          'cleanup': 'pending'
      - type: notify
        to: ['platform@example.com']</code></pre>
<p>After the resource owner reviews the flag, a second pass performs
the actual deletion — never automatic on the first pass, to avoid
deleting something that was actually still in legitimate use.</p>

<h3>6. Auto-scaling as FinOps</h3>
<p>Provisioning fixed capacity for the expected peak means paying for
the peak the ENTIRE time, even during low-traffic hours — auto-scaling
solves this by adjusting capacity dynamically according to real
demand. The EC2 Auto Scaling Group does target tracking (keeping
average CPU at, say, 60%). The Kubernetes HPA (Horizontal Pod
Autoscaler) scales pods based on a custom metric. The Cluster
Autoscaler or Karpenter in Kubernetes adds or removes entire NODES as
pending pods appear or disappear. Lambda scales to zero when nobody's
calling the function. And Fargate charges only for the container
actually running, scaling from zero to N without managing any server
behind it. Karpenter deserves specific mention: it provisions the
exact node for the pod that needs it — choosing Spot when possible and
the right family/size for that specific workload — delivering
substantial savings compared to the classic Cluster Autoscaler, which
works with a more generic instance group.</p>

<h3>7. Egress, NAT Gateway, and the invisible costs</h3>
<table>
<tr><th>Item</th><th>$/unit</th><th>Impact estimate</th></tr>
<tr><td>Traffic leaving AWS</td><td>~$0.09/GB</td>
<td>video-serving app: $$$</td></tr>
<tr><td>Cross-region traffic</td><td>~$0.02/GB</td>
<td>careless replication</td></tr>
<tr><td>Cross-AZ traffic</td><td>~$0.01/GB</td>
<td>K8s app without topology-aware routing</td></tr>
<tr><td>NAT Gateway</td><td>~$32/month + $0.045/GB</td>
<td>private → internet, expensive</td></tr>
<tr><td>VPC Endpoint Interface</td><td>~$7/month per AZ</td>
<td>expensive at scale but can be worth it</td></tr>
</table>
<p>Five mitigations reduce this category of silent cost: VPC Endpoint
Gateway for S3 and DynamoDB (free, and already covered in detail in
the VPC lesson); CloudFront charging a lower price per GB than direct
egress; HTTP compression (gzip, brotli) reducing the actual volume
transferred; edge caching avoiding repeating the same transfer
multiple times; and topology-aware routing in Kubernetes, prioritizing
traffic within the same AZ before crossing to another one.</p>

<h3>8. Budgets, alerts, and quotas</h3>
<p>Setting this up BEFORE the first deploy — not after the first
scare — is what separates a managed bill from an end-of-month
surprise:</p>
<pre><code>resource "aws_budgets_budget" "monthly" {
  name         = "prod-monthly"
  budget_type  = "COST"
  limit_amount = "5000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 50
    threshold_type      = "PERCENTAGE"
    notification_type   = "FORECASTED"
    subscriber_email_addresses = ["finance@example.com"]
  }
  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 90
    notification_type   = "ACTUAL"
    subscriber_email_addresses = ["oncall@example.com"]
  }
}</code></pre>
<p>In a sandbox account specifically, it's worth considering AWS
Budget Actions — applying an SCP that automatically denies
<code>RunInstances</code> upon reaching 100% of the configured budget,
preventing a bug in a loop (like the Dutch journalist case from the
previous lesson) from having any chance to blow up with no practical
limit.</p>

<h3>9. FinOps culture: Crawl / Walk / Run</h3>
<p>The FinOps Foundation defines three progressive maturity stages,
and skipping a stage is the most common mistake. In the
<strong>Crawl</strong> stage, the focus is basic visibility: tags,
Cost Explorer, a configured budget, a simple KPI being tracked. In
<strong>Walk</strong>, continuous optimization comes in: automated
right-sizing, showback per team (each team seeing its own cost), and
cost anomaly detection. In <strong>Run</strong>, PRODUCT decisions are
already directly influenced by cost: real chargeback between areas,
forecasting integrated into planning, and unit economics calculated
per transaction (<code>$ / transaction</code>). Without solid basic
visibility from Crawl established first, any attempt at "optimization"
in the following stage ends up based on distorted or incomplete
data.</p>

<h3>10. Real case: Fly.io and the unexpected bill</h3>
<p>In 2024, Fly.io published a public postmortem about a customer
whose VM entered a crash loop, generating 50 TB of cross-region
transfer in just two days — a projected bill of $70 thousand. The
lessons documented from the incident: the customer had a budget
configured, but never got around to configuring the corresponding
ALERT, making the budget useless in practice; the loop took 18 hours
to be detected by the team itself; Fly.io absorbed 80% of the cost as
a goodwill gesture toward the customer; the lesson Fly.io took away
was to apply egress rate-limiting by default on new accounts,
preventing the same structural scenario; and the lesson on the
customer's side was to configure an alert specifically on "traffic per
minute above X" — the kind of signal that would have detected the
problem in minutes, not hours.</p>

<h3>11. Anti-patterns</h3>
<ul>
<li><strong>Buying a 3-year Reserved Instance without analyzing usage
patterns</strong>: locks in a long commitment based on an unverified
assumption.</li>
<li><strong>Not using tags, every resource becomes "misc"</strong>:
eliminates the visibility that any informed decision depends on
(section 2).</li>
<li><strong>No retention configured in CloudWatch Logs</strong>: grows
indefinitely with no limit, one of the most common orphans
(section 5).</li>
<li><strong>Daily snapshot of everything with no expiration</strong>:
accumulates storage cost with no real retention limit.</li>
<li><strong>Provisioning a large instance "to be safe" without
measuring</strong>: exactly the pattern that right-sizing (section 4)
exists to correct.</li>
<li><strong>Spot for stateful workloads without checkpointing</strong>:
loses all progress on every interruption with only 2 minutes of
notice.</li>
<li><strong>No anomaly alert configured</strong>: Cost Anomaly
Detection is free on AWS and rarely gets enabled even so.</li>
<li><strong>Finance team without access to Cost Explorer</strong>:
whoever needs the cost data most ends up without direct access to
it.</li>
<li><strong>Showback that nobody looks at</strong>: generating the
report isn't enough if it doesn't influence any team's real
decision.</li>
</ul>"""
                ),
                "practical": (
                    "(1) Ative cost allocation tags em sua conta AWS. Adicione tag "
                    "<code>Environment</code> e <code>Owner</code> em pelo menos 5 "
                    "recursos.<br>"
                    "(2) Em Cost Explorer, identifique os 3 serviços que mais custam no "
                    "último mês.<br>"
                    "(3) Para cada um, escreva 1 ação concreta:<br>"
                    "&nbsp;&nbsp;• Para EC2: rodar Compute Optimizer, considerar Graviton "
                    "ou Spot.<br>"
                    "&nbsp;&nbsp;• Para NAT Gateway: configurar VPC Endpoints para S3.<br>"
                    "&nbsp;&nbsp;• Para CloudWatch Logs: configurar retention "
                    "(<code>14d</code> em dev, <code>90d</code> em prod).<br>"
                    "(4) Configure budget alert em 50% e 90% via AWS Budgets.<br>"
                    "(5) Configure Cost Anomaly Detection (free) em sua conta.<br>"
                    "(6) Bônus: instale Komiser via docker-compose e veja o relatório "
                    "consolidado de custo + recursos órfãos."
                ),
                "practical_en": (
                    "(1) Enable cost allocation tags on your AWS account. Add the "
                    "<code>Environment</code> and <code>Owner</code> tags to at least 5 "
                    "resources.<br>"
                    "(2) In Cost Explorer, identify the 3 services that cost the most in the "
                    "last month.<br>"
                    "(3) For each one, write 1 concrete action:<br>"
                    "&nbsp;&nbsp;• For EC2: run Compute Optimizer, consider Graviton or "
                    "Spot.<br>"
                    "&nbsp;&nbsp;• For NAT Gateway: configure VPC Endpoints for S3.<br>"
                    "&nbsp;&nbsp;• For CloudWatch Logs: configure retention "
                    "(<code>14d</code> in dev, <code>90d</code> in prod).<br>"
                    "(4) Configure a budget alert at 50% and 90% via AWS Budgets.<br>"
                    "(5) Configure Cost Anomaly Detection (free) on your account.<br>"
                    "(6) Bonus: install Komiser via docker-compose and see the consolidated "
                    "cost + orphaned resources report."
                ),
            },
            "materials": [
                m("FinOps Foundation", "https://www.finops.org/", "article", "",
                  title_en="FinOps Foundation", description_en=""),
                m("AWS Cost Optimization",
                  "https://aws.amazon.com/aws-cost-management/", "docs", "",
                  title_en="AWS Cost Optimization", description_en=""),
                m("Azure Cost Management",
                  "https://learn.microsoft.com/azure/cost-management-billing/cost-management-billing-overview",
                  "docs", "", title_en="Azure Cost Management", description_en=""),
                m("GCP cost optimization",
                  "https://cloud.google.com/architecture/framework/cost-optimization",
                  "docs", "", title_en="GCP cost optimization", description_en=""),
                m("Komiser (OSS)", "https://github.com/tailwarden/komiser",
                  "tool", "", title_en="Komiser (OSS)", description_en=""),
                m("Cloud Custodian",
                  "https://cloudcustodian.io/", "tool",
                  "Policies as code para limpeza automatizada.",
                  title_en="Cloud Custodian",
                  description_en="Policies as code for automated cleanup."),
            ],
            "questions": [
                q("Tag obrigatória recomendada:",
                  "Owner, Environment, CostCenter.",
                  ["Só o nome do recurso, sem outra informação de contexto associada.",
                   "Só a região onde o recurso está hospedado, sem mais contexto.",
                   "Só o tipo do recurso, sem indicar quem é responsável por ele."],
                  "Sem tags consistentes, atribuição de custo vira política em vez de matemática.",
                  statement_en="Recommended mandatory tag:",
                  correct_en="Owner, Environment, CostCenter.",
                  wrong_en=["Only the resource's name, with no other associated context.",
                            "Only the region where the resource is hosted, with no more context.",
                            "Only the resource's type, without indicating who's responsible for it."],
                  explanation_en="Without consistent tags, cost attribution becomes politics instead of math."),
                q("Spot Instance é:",
                  "VM barata que pode ser interrompida.",
                  ["Uma VM de linha premium, com garantia de disponibilidade total.",
                   "Um disco SSD de alta performance usado para armazenamento.",
                   "Um tipo de role dentro do sistema de IAM da conta."],
                  "Aviso de 2 minutos antes da interrupção. Ideal para batch, CI, treino de ML.",
                  statement_en="A Spot Instance is:",
                  correct_en="A cheap VM that can be interrupted.",
                  wrong_en=["A premium-tier VM, with a guarantee of total availability.",
                            "A high-performance SSD disk used for storage.",
                            "A type of role inside the account's IAM system."],
                  explanation_en="2-minute warning before interruption. Ideal for batch, CI, ML training."),
                q("Reserved Instance dá desconto se:",
                  "Você se compromete por 1 ou 3 anos.",
                  ["Pagar o valor à vista, com desconto aplicado enquanto durar o contrato.",
                   "Usar IPv6 em vez de IPv4 na configuração de rede da instância.",
                   "Deixar a instância parada durante boa parte do período contratado."],
                  "Savings Plans são mais flexíveis (qualquer family/region) com desconto similar.",
                  statement_en="A Reserved Instance gives a discount if:",
                  correct_en="You commit for 1 or 3 years.",
                  wrong_en=["Paying upfront, with the discount applied for the life of the contract.",
                            "Using IPv6 instead of IPv4 in the instance's network configuration.",
                            "Leaving the instance stopped for most of the contracted period."],
                  explanation_en="Savings Plans are more flexible (any family/region) with a similar discount."),
                q("Recurso órfão é:",
                  "Recurso sem uso que ainda é cobrado (ex.: snapshot antigo).",
                  ["Um recurso que apresenta erro recorrente durante a execução.",
                   "Um recurso criado especificamente para ambiente de teste.",
                   "Um recurso sem dono definido dentro do IAM da conta."],
                  "Use Cloud Custodian para detectar e remediar (ex.: deletar snapshots > 90d).",
                  statement_en="An orphaned resource is:",
                  correct_en="A resource with no use that's still being charged (e.g., an old snapshot).",
                  wrong_en=["A resource that shows a recurring error during every scheduled execution attempt.",
                            "A resource created specifically for a test environment.",
                            "A resource with no defined owner inside the account's IAM."],
                  explanation_en="Use Cloud Custodian to detect and remediate it (e.g., delete snapshots older than 90 days)."),
                q("Right-sizing é:",
                  "Ajustar tamanho de instâncias ao uso real.",
                  ["Escolher o menor tamanho disponível, independente do uso real.",
                   "Escolher o maior tamanho disponível, por segurança extra.",
                   "Só ajustar a largura do disco, sem tocar no tamanho da instância."],
                  "Ferramentas mostram CPU/memória médio e sugerem família/tamanho menor.",
                  statement_en="Right-sizing is:",
                  correct_en="Adjusting instance size to match real usage.",
                  wrong_en=["Choosing the smallest size available, regardless of real usage.",
                            "Choosing the largest size available, for extra safety.",
                            "Merely adjusting the disk width, without touching the instance size."],
                  explanation_en="Tools show average CPU/memory and suggest a smaller family/size."),
                q("Budget alerts servem para:",
                  "Avisar antes do orçamento estourar.",
                  ["Reduzir a latência percebida pelo usuário final da aplicação.",
                   "Aumentar a cota disponível automaticamente sem intervenção humana.",
                   "Acelerar o tempo de deploy de uma aplicação nova em produção."],
                  "Configure alertas em 50%/80%/100% para evitar surpresa no fim do mês.",
                  statement_en="Budget alerts serve to:",
                  correct_en="Warn before the budget is blown.",
                  wrong_en=["Reduce latency perceived by the application's end user.",
                            "Automatically increase the available quota with no human intervention.",
                            "Speed up deploy time for a new application in production."],
                  explanation_en="Configure alerts at 50%/80%/100% to avoid an end-of-month surprise."),
                q("FinOps maturity vai do crawl ao:",
                  "Run.",
                  ["Sprint.",
                   "Spawn.",
                   "Stop."],
                  "Crawl (visibilidade) → Walk (otimização contínua) → Run (decisões de produto).",
                  statement_en="FinOps maturity goes from crawl to:",
                  correct_en="Run.",
                  wrong_en=["Sprint.",
                            "Spawn.",
                            "Stop."],
                  explanation_en="Crawl (visibility) → Walk (continuous optimization) → Run (product decisions)."),
                q("Para batches diários:",
                  "Considere Spot/Preemptible.",
                  ["Usar on-demand de forma contínua, mesmo topando pagar o preço cheio.",
                   "Rodar em hardware próprio, fora de qualquer provedor de nuvem.",
                   "Contratar Reserved Instance de 3 anos para uma carga esporádica."],
                  "Batch tolera interrupção; spot economiza até 90% comparado a on-demand.",
                  statement_en="For daily batches:",
                  correct_en="Consider Spot/Preemptible.",
                  wrong_en=["Using on-demand continuously, even if it means paying full price.",
                            "Running on your own hardware, outside any cloud provider.",
                            "Contracting a 3-year Reserved Instance for a sporadic workload."],
                  explanation_en="Batch tolerates interruption; spot saves up to 90% compared to on-demand."),
                q("Auto Scaling reduz custo porque:",
                  "Provisiona apenas quando há demanda.",
                  ["Aumenta a cota de recurso disponível para a conta inteira.",
                   "Substitui a política de IAM aplicada à instância provisionada.",
                   "Libera uma configuração de segurança adicional na conta."],
                  "Combine com warm pool para reduzir cold start e ainda economizar.",
                  statement_en="Auto Scaling reduces cost because:",
                  correct_en="It provisions only when there's demand.",
                  wrong_en=["It increases the resource quota available for the entire account.",
                            "It replaces the IAM policy applied only to the provisioned instance.",
                            "It unlocks an additional security configuration on the account."],
                  explanation_en="Combine with a warm pool to reduce cold start and still save money."),
                q("Showback vs chargeback:",
                  "Showback mostra; chargeback cobra internamente.",
                  ["São a mesma prática, só com nome diferente entre empresa.",
                   "Uma invenção sem uso real dentro da prática de FinOps.",
                   "Os dois cobram diretamente o cliente externo da empresa."],
                  "Showback gera consciência. Chargeback cria accountability, recomendado em "
                  "estágios mais maduros de FinOps.",
                  statement_en="Showback vs chargeback:",
                  correct_en="Showback shows the cost; chargeback bills it internally.",
                  wrong_en=["The same practice, just called differently between companies.",
                            "A made-up concept with no real use in FinOps practice.",
                            "Both of them bill the company's external customer directly."],
                  explanation_en="Showback builds awareness. Chargeback creates accountability, recommended in more mature FinOps stages."),
            ],
        },
    ],
}
