"""Fase 2, Introdução à Nuvem (Cloud Essentials)."""
from ._helpers import m, q

PHASE2 = {
    "name": "Fase 2: Introdução à Nuvem (Cloud Essentials)",
    "description": "Saindo do servidor físico/local para recursos sob demanda.",
    "topics": [
        # =====================================================================
        # 2.1 Virtualização vs. Cloud
        # =====================================================================
        {
            "title": "Virtualização vs. Cloud",
            "summary": "Como a nuvem abstrai o hardware e o que muda em relação a VMs tradicionais.",
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
            },
            "materials": [
                m("AWS What is cloud computing?",
                  "https://aws.amazon.com/what-is-cloud-computing/", "article", ""),
                m("KVM Documentation",
                  "https://www.linux-kvm.org/page/Documents", "docs", ""),
                m("Microsoft: Cloud computing dictionary",
                  "https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/",
                  "article", ""),
                m("Container vs VM (Docker)",
                  "https://www.docker.com/resources/what-container/", "article", ""),
                m("CNCF Glossary", "https://glossary.cncf.io/", "docs",
                  "Mantém termos atualizados de cloud-native."),
                m("Linux Foundation: Open source cloud landscape",
                  "https://landscape.cncf.io/", "tool", ""),
            ],
            "questions": [
                q("O que é um hypervisor tipo 1?",
                  "Roda direto no hardware, sem SO host.",
                  ["É um tipo de container isolado por namespace do kernel.",
                   "Substitui o BIOS da placa-mãe por um firmware customizado.",
                   "Roda dentro de outro sistema operacional já instalado antes."],
                  "Tipo 1 = bare-metal (KVM, ESXi, Hyper-V). Tipo 2 = roda como app dentro de "
                  "outro SO (VirtualBox)."),
                q("Cloud difere de virtualização porque:",
                  "Adiciona APIs, self-service e billing por uso.",
                  ["Não usa hardware físico algum durante a execução da carga.",
                   "Não oferece suporte ao sistema operacional Linux em seu catálogo.",
                   "Não tem rede alguma conectando os servidores do datacenter."],
                  "Virtualização é fundação técnica; cloud junta automação, multi-tenancy e billing."),
                q("VM e container compartilham:",
                  "O hardware via virtualização (mesmo host físico).",
                  ["O mesmo hypervisor rodando abaixo de ambos ao mesmo tempo.",
                   "O mesmo kernel do sistema operacional hospedeiro compartilhado.",
                   "O mesmo endereço IP público atribuído à interface de rede."],
                  "Containers compartilham kernel; VMs têm kernel próprio. Ambos podem rodar no mesmo host."),
                q("Vantagem de cloud para startups:",
                  "Capex baixo e elasticidade.",
                  ["Hardware proprietário.",
                   "Sem necessidade de monitoramento.",
                   "Latência zero."],
                  "Pay-as-you-go evita compra de hardware para pico que pode nem existir."),
                q("Tipo de cloud onde recursos são exclusivos da empresa:",
                  "Private cloud.",
                  ["Edge cloud, computação posicionada fisicamente perto do usuário final.",
                   "Hybrid cloud, combinação de nuvem pública e privada ao mesmo tempo.",
                   "Public cloud, infraestrutura compartilhada entre múltiplos clientes diferentes."],
                  "Pode ser on-premise (datacenter próprio) ou VPC dedicada num provedor público."),
                q("Qual hypervisor é open source e parte do kernel Linux?",
                  "KVM",
                  ["VMware ESXi", "Hyper-V", "Xen Server proprietary"],
                  "KVM ('Kernel-based Virtual Machine') é módulo do kernel; libvirt e QEMU "
                  "completam o ecossistema."),
                q("'Pay-as-you-go' refere-se a:",
                  "Cobrar pelo uso real, sem compromisso de longo prazo.",
                  ["Pagar o valor inteiro antecipado antes de sequer usar o serviço.",
                   "Usar o serviço de graça enquanto ele estiver ativo e funcionando.",
                   "Pagar só se o projeto for bem-sucedido no fim do ano."],
                  "Em muitos serviços (S3, Lambda, Run) você paga por requisição/byte. Em VMs, por hora/segundo."),
                q("Multi-tenancy implica:",
                  "Múltiplos clientes compartilhando infra com isolamento.",
                  ["Banco de dados único, sem separação lógica entre registro de cliente diferente.",
                   "Ausência completa de segregação entre carga de trabalho diferente.",
                   "Só um cliente autorizado a usar cada servidor físico por vez."],
                  "Isolamento via namespaces, IAM, redes virtuais. Provedor garante que tenant A não vê tenant B."),
                q("Region em cloud é:",
                  "Conjunto geográfico de datacenters (várias AZs).",
                  ["Um endereço IP público atribuído a uma única instância específica.",
                   "Uma role de IAM concedendo permissão de acesso a um recurso.",
                   "Uma máquina física específica dentro de um datacenter qualquer."],
                  "Ex.: us-east-1 tem múltiplas AZs (us-east-1a, 1b, 1c). Latência baixa entre AZs, alta entre regiões."),
                q("Disponibilidade aumenta com:",
                  "Distribuir cargas entre múltiplas Availability Zones.",
                  ["Reduzir o número de réplica ativa para economizar custo de operação.",
                   "Fazer backup periódico só do banco de dados principal da aplicação.",
                   "Usar um único disco SSD de alta performance sem redundância alguma."],
                  "AZ é falha unitária, se uma cair, as outras sobrevivem se você arquitetou multi-AZ."),
            ],
        },
        # =====================================================================
        # 2.2 Shared Responsibility Model
        # =====================================================================
        {
            "title": "Shared Responsibility Model",
            "summary": "O que é dever da AWS/Azure/GCP e o que é seu.",
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
                "body": (
                """<h3>1. A linha móvel: quanto mais alto o serviço, mais o provedor cobre</h3>
<p>A divisão de responsabilidade muda de acordo com o nível de
abstração escolhido:</p>
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
            },
            "materials": [
                m("AWS Shared Responsibility Model",
                  "https://aws.amazon.com/compliance/shared-responsibility-model/", "docs", ""),
                m("Azure Shared Responsibility",
                  "https://learn.microsoft.com/azure/security/fundamentals/shared-responsibility",
                  "docs", ""),
                m("Google: Shared responsibility on Google Cloud",
                  "https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate",
                  "docs", ""),
                m("CIS Benchmarks", "https://www.cisecurity.org/cis-benchmarks/", "docs", ""),
                m("CSA Cloud Controls Matrix",
                  "https://cloudsecurityalliance.org/research/cloud-controls-matrix/", "docs", ""),
                m("Verizon DBIR (relatório anual)",
                  "https://www.verizon.com/business/resources/reports/dbir/", "article", ""),
            ],
            "questions": [
                q("Em IaaS, quem é responsável pelo SO da VM?",
                  "O cliente.",
                  ["O provedor.", "Compartilhado 50/50.", "Ninguém."],
                  "Cliente responde por patch, configuração, agentes. Provedor só fornece o substrato físico."),
                q("O provedor de cloud é responsável por:",
                  "Segurança DA cloud (datacenter, hypervisor).",
                  ["Aplicar patch de segurança na aplicação do cliente rodando ali.",
                   "Configurar a política de IAM específica da conta do cliente.",
                   "Fazer backup do banco de dados que pertence ao cliente final."],
                  "DA cloud (segurança da infraestrutura) é do provedor; NA cloud (o que você roda nela) é seu."),
                q("Em SaaS típico, o que ainda é dever do cliente?",
                  "Identidades, dados e configuração.",
                  ["O hardware físico do datacenter onde o serviço realmente roda.",
                   "O sistema operacional completo da máquina virtual subjacente.",
                   "O hypervisor que isola cada cliente dentro do mesmo servidor físico."],
                  "Mesmo no SaaS, gerência de usuários, MFA e classificação de dados não saem do cliente."),
                q("Quem responde por uma S3 mal configurado e público?",
                  "O cliente, é configuração dele.",
                  ["É um bug conhecido da própria AWS, sem relação com configuração.",
                   "O provedor assume, porque o bucket nasce protegido por padrão.",
                   "Responsabilidade dividida meio a meio entre cliente e provedor."],
                  "AWS oferece 'Block Public Access' habilitado por padrão; cliente desligou? Cliente respondeu."),
                q("Backup de dados em RDS é dever:",
                  "Do cliente, a AWS oferece a infraestrutura, mas o cliente configura snapshots e retenção.",
                  ["Do provedor, que garante backup automático completo em cada instância RDS criada por padrão de fábrica.",
                   "Da equipe de auditoria externa contratada especificamente para essa tarefa periódica de revisão.",
                   "RDS não oferece forma de backup automatizado ou manual disponível em qualquer plano contratado."],
                  "Snapshots automáticos têm retenção padrão curta; ajuste para sua janela de RTO/RPO."),
                q("Qual fator NÃO faz parte do shared responsibility?",
                  "Cor do logo da empresa.",
                  ["Identidade do usuário e política de acesso configurada por ele.",
                   "Dado armazenado e processado dentro de qualquer um dos serviços.",
                   "Rede virtual (VPC) e as regras de roteamento definidas pelo cliente."],
                  "Pegadinha, todos os outros são partes legítimas do modelo."),
                q("Em IaaS, patch do kernel é:",
                  "Responsabilidade do cliente.",
                  ["Responsabilidade do provedor.",
                   "Não precisa ser feito.",
                   "Automatizado pela cloud."],
                  "Use Systems Manager/Update Management para automatizar, mas a responsabilidade é sua."),
                q("Compliance é responsabilidade:",
                  "Compartilhada, cada parte certifica o que controla.",
                  ["Só do auditor externo contratado uma vez por ano pela empresa.",
                   "Só do provedor de nuvem, que certifica o datacenter inteiro sozinho.",
                   "Só do cliente, que precisa provar conformidade sem qualquer ajuda do provedor contratado."],
                  "Provedor mostra que o datacenter está conforme; cliente mostra que sua app/processo está conforme."),
                q("Por que ler documentos do provedor?",
                  "Para saber o limite exato e não pressupor cobertura.",
                  ["Por exigência legal, sem motivo prático adicional relevante para o negócio.",
                   "Para virar parceiro comercial oficial certificado pelo provedor.",
                   "Para reduzir o custo mensal pago pela licença do serviço contratado."],
                  "Surpresas em incidente são caras; ler antes evita 'nossa, achei que vocês cuidassem disso'."),
                q("Configuração errada em segurança em cloud é a causa:",
                  "Mais comum de incidentes em cloud pública.",
                  ["Mais rara do que ataque direto à infraestrutura do provedor.",
                   "Atribuída exclusivamente ao provedor, independente da configuração do cliente.",
                   "Um problema restrito só à área de billing e cobrança do contrato."],
                  "Confirmado por DBIR, CSA, Gartner, AWS Well-Architected, misconfiguration domina o ranking."),
            ],
        },
        # =====================================================================
        # 2.3 IAM
        # =====================================================================
        {
            "title": "IAM (Identity and Access Management)",
            "summary": "Criação de usuários, grupos e roles com permissões restritas.",
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
            },
            "materials": [
                m("AWS IAM Best Practices",
                  "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
                  "docs", ""),
                m("Azure RBAC overview",
                  "https://learn.microsoft.com/azure/role-based-access-control/overview",
                  "docs", ""),
                m("GCP IAM overview",
                  "https://cloud.google.com/iam/docs/overview", "docs", ""),
                m("Cloudonaut: IAM tutorials",
                  "https://cloudonaut.io/", "article", ""),
                m("AWS Policy Simulator",
                  "https://policysim.aws.amazon.com/", "tool", ""),
                m("GitHub OIDC for AWS",
                  "https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services",
                  "docs", "Substituir chave estática por OIDC."),
            ],
            "questions": [
                q("Vantagem de role sobre chave estática:",
                  "Credenciais temporárias, sem armazenamento persistente.",
                  ["Custa menos, porque cobra por hora em vez de mensalidade fixa.",
                   "Cota maior de requisição por segundo concedida a esse tipo de credencial.",
                   "Handshake mais rápido do que o de uma credencial estática comum."],
                  "Chave temporária expira sozinha; chave estática vaza e fica em open-source forever."),
                q("MFA serve para:",
                  "Adicionar segundo fator (algo que você tem) à autenticação.",
                  ["Substitui a senha por completo, eliminando a etapa de digitá-la.",
                   "Aumenta a cota de requisição disponível para aquele usuário específico.",
                   "Gera um token de DNS usado para provar propriedade de domínio."],
                  "Reduz drasticamente o risco de credential stuffing, mesmo se a senha vaza, MFA segura."),
                q("Policy IAM é avaliada como:",
                  "Combinação de Allow/Deny, Deny sempre vence em conflito.",
                  ["A última regra escrita no arquivo de política vence sobre as demais.",
                   "Considera só o Allow mais recente adicionado à política do usuário.",
                   "Escolhida de forma aleatória entre as regras aplicáveis ao caso, sem critério fixo."],
                  "Sem Allow explícito, default é negar. Deny sempre wins, mesmo se houver Allow em outra policy."),
                q("Para devs sem precisar de console, prefira:",
                  "Roles e federação (IAM Identity Center / SSO).",
                  ["Usuário do IAM com uma chave de acesso de longa duração.",
                   "Compartilhar a mesma credencial entre vários desenvolvedores do time.",
                   "Senha enviada por SMS a cada tentativa de login do usuário."],
                  "Acesso temporário emitido por SSO; nada de chave longa flutuando em ~/.aws/credentials."),
                q("SCP em AWS Organizations serve para:",
                  "Criar guardrails que limitam o que contas filhas podem fazer.",
                  ["Substituir a VPC inteira da conta por uma rede gerenciada completamente diferente.",
                   "Acelerar o tempo de deploy de uma aplicação específica dentro da conta.",
                   "Aumentar o valor total cobrado mensalmente na fatura consolidada da conta."],
                  "SCP é teto: mesmo Admin de uma sub-conta não escapa. Útil para impor compliance."),
                q("Por que rotacionar access keys?",
                  "Limita o impacto se uma chave vazar.",
                  ["Reduz o custo mensal pago pelo uso da credencial na conta.",
                   "Necessário para o protocolo HTTPS funcionar corretamente na API.",
                   "Aumenta a velocidade de resposta da chamada de API feita."],
                  "Janela de exploração de uma chave vazada é o tempo entre vazamento e próxima rotação."),
                q("Como aplicar PoLP em IAM?",
                  "Conceder apenas as ações e recursos estritamente necessários.",
                  ["Ignorar a política existente e criar uma nova do zero.",
                   "Permitir tudo logo no início e restringir depois aos poucos.",
                   "Conceder AdministratorAccess de saída para simplificar o setup."],
                  "Comece restrito; relaxe só se a app realmente precisar. Use Access Analyzer para encontrar excessos."),
                q("Qual recurso registra quem fez o quê na AWS?",
                  "AWS CloudTrail.",
                  ["Athena, usado para consultar dado já armazenado, não para gerar log.",
                   "VPC Flow Logs, que registra tráfego de rede, não chamada de API.",
                   "Log do S3 sozinho, que cobre só aquele bucket específico."],
                  "CloudTrail registra calls de API. Habilitar org-wide trail e enviar para bucket protegido."),
                q("Diferença entre user e role:",
                  "User tem credenciais permanentes; role é assumida temporariamente.",
                  ["Um usuário só pode ser usado por pessoa humana, jamais por máquina automatizada.",
                   "Assumir uma role custa mais caro do que manter um usuário fixo.",
                   "Uma role está reservada só para máquina, sem uso possível por humano."],
                  "Humano pode assumir role via SSO; máquina via STS AssumeRole. Ambos podem."),
                q("Recomendação para conta root:",
                  "Não usar para tarefas diárias e ativar MFA forte.",
                  ["Desativar completamente o MFA para agilizar o acesso diário.",
                   "Compartilhar a senha da conta root com o time de operação inteiro.",
                   "Usar a conta root para qualquer tarefa do dia a dia, sem restrição."],
                  "Use root só para tarefas que exigem (alterar conta, fechar). MFA hardware ideal."),
            ],
        },
        # =====================================================================
        # 2.4 VPC & Subnets
        # =====================================================================
        {
            "title": "VPC & Subnets",
            "summary": "Criar seu próprio 'pedaço' de rede isolado na nuvem.",
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
            },
            "materials": [
                m("AWS VPC User Guide",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
                  "docs", ""),
                m("Azure Virtual Network",
                  "https://learn.microsoft.com/azure/virtual-network/virtual-networks-overview",
                  "docs", ""),
                m("GCP VPC overview",
                  "https://cloud.google.com/vpc/docs/overview", "docs", ""),
                m("AWS Networking Workshop",
                  "https://catalog.workshops.aws/networking/en-US", "course", ""),
                m("CIDR Calculator", "https://cidr.xyz/", "tool", ""),
                m("VPC Endpoints (AWS)",
                  "https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html",
                  "docs", ""),
            ],
            "questions": [
                q("Subnet privada NÃO tem:",
                  "Rota para Internet Gateway.",
                  ["Tabela de rota associada à subnet, controlando o destino do pacote.",
                   "Endereço IP atribuído a cada interface de rede dentro da subnet.",
                   "Security Group aplicado à instância que vive dentro da subnet."],
                  "Sem rota para IGW, instâncias não recebem tráfego direto da internet."),
                q("Para outbound de subnet privada:",
                  "Use NAT Gateway.",
                  ["Use o Internet Gateway de forma direta, pulando qualquer intermediário no caminho.",
                   "Use Direct Connect, uma linha dedicada até o datacenter próprio.",
                   "Não é possível ter saída de internet numa subnet privada dessa forma."],
                  "NAT Gateway permite saída sem expor a instância. Caro: considere VPC Endpoint quando o destino é AWS."),
                q("CIDR /16 em AWS VPC permite quantos hosts aproximadamente?",
                  "65 mil",
                  ["256", "1024", "infinitos"],
                  "/16 = 2^16 = 65.536 endereços. Subdivida em /24 (256 cada) ou /22, conforme necessidade."),
                q("VPC Peering serve para:",
                  "Conectar duas VPCs com IPs distintos.",
                  ["Cobrar valor adicional na fatura mensal de uma conta específica.",
                   "Substituir a resolução de nome feita normalmente pelo DNS interno.",
                   "Conectar container dentro do mesmo host, sem envolver rede alguma."],
                  "Peering é 1:1. Para muitas VPCs, use Transit Gateway (hub-and-spoke)."),
                q("Por que múltiplas AZs?",
                  "Resiliência a falhas de datacenter inteiro.",
                  ["Reduz o custo mensal pago pela infraestrutura de rede utilizada.",
                   "Aumenta a latência entre instância dentro da mesma aplicação.",
                   "Não é uma prática recomendada para ambiente de produção real."],
                  "AZ é unidade de falha; deploy multi-AZ é o mínimo para serviços de produção."),
                q("Route table define:",
                  "Para onde pacotes de uma subnet vão.",
                  ["Versão do protocolo TLS aceito pela conexão HTTPS da aplicação.",
                   "Permissão do IAM concedida a um usuário ou role específico.",
                   "Tamanho máximo do pacote (MTU) aceito por uma interface de rede."],
                  "Cada destino (CIDR) tem next-hop (IGW, NAT, peering, gateway endpoint, etc.)."),
                q("Endpoint VPC para S3 reduz:",
                  "Tráfego que sai pela internet, vai pela rede da AWS.",
                  ["Latência para qualquer destino fora da infraestrutura da AWS.",
                   "Necessidade de configurar IAM para acessar o bucket do S3.",
                   "O custo cobrado pelo armazenamento de dado dentro do S3."],
                  "Custos de NAT despencam e exposição também. Use Gateway Endpoint para S3/DynamoDB."),
                q("Internet Gateway é:",
                  "Recurso que permite conectividade bidirecional pública.",
                  ["Um proxy reverso que intermedia a conexão entre cliente e servidor.",
                   "Um firewall que filtra pacote antes dele chegar à instância.",
                   "Um recurso exclusivo para tráfego IPv6, sem suporte a IPv4."],
                  "IGW associado à VPC + rota 0.0.0.0/0 → IGW na route table = subnet pública."),
                q("Em VPC, qual recurso é stateful?",
                  "Security Groups.",
                  ["Route Tables, que definem destino, não estado de conexão.",
                   "Subnets, que são só blocos de IP dentro da VPC, sem estado.",
                   "NACLs, que filtram tráfego sem lembrar o estado da conexão."],
                  "SG entende a conexão (stateful). NACL é stateless, precisa configurar inbound E outbound."),
                q("CIDR sobreposto entre VPCs causa:",
                  "Problema em peering, não é permitido.",
                  ["Backup automático configurado entre as duas VPCs envolvidas.",
                   "Aceleração real do tráfego entre as duas VPCs conectadas.",
                   "Alta disponibilidade extra para a aplicação rodando ali."],
                  "Pacotes não saberiam para qual VPC ir. Planeje CIDRs com IP plan global."),
            ],
        },
        # =====================================================================
        # 2.5 Security Groups & ACLs
        # =====================================================================
        {
            "title": "Security Groups & ACLs",
            "summary": "O firewall da nuvem protegendo suas instâncias.",
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
            },
            "materials": [
                m("AWS Security Groups",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html",
                  "docs", ""),
                m("AWS NACLs",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html",
                  "docs", ""),
                m("Azure NSG",
                  "https://learn.microsoft.com/azure/virtual-network/network-security-groups-overview",
                  "docs", ""),
                m("GCP Firewall Rules",
                  "https://cloud.google.com/firewall/docs/firewalls", "docs", ""),
                m("Cloudflare: stateful vs stateless firewall",
                  "https://www.cloudflare.com/learning/network-layer/what-is-a-stateful-firewall/",
                  "article", ""),
                m("AWS SSM Session Manager",
                  "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html",
                  "docs", "Substitui bastion+SSH em muitos casos."),
            ],
            "questions": [
                q("Security Group em AWS é:",
                  "Stateful, resposta automática.",
                  ["Stateless, precisa de regra separada para tráfego de resposta.",
                   "Aplicado por host físico inteiro, não por interface de rede individual.",
                   "Restrito só a tráfego IPv6, sem suporte a IPv4 disponível."],
                  "Stateful = inbound libera o retorno do outbound automaticamente. NACL é o oposto."),
                q("NACL em AWS é:",
                  "Stateless, precisa regras de saída e entrada.",
                  ["Restrito só ao protocolo IPv4, sem cobertura para tráfego IPv6.",
                   "Aplicado à instância inteira, não à interface de rede especificamente.",
                   "Stateful, libera resposta automaticamente sem regra adicional."],
                  "Esquecer regra outbound de portas efêmeras é fonte clássica de 'meu serviço não responde'."),
                q("Por padrão, SG inbound:",
                  "Bloqueia tudo.",
                  ["Libera acesso só pela porta usada pelo protocolo SSH.",
                   "Permite qualquer tráfego de entrada, sem restrição alguma configurada previamente.",
                   "Aceita conexão nas portas 80 e 443 por padrão de fábrica."],
                  "Default-deny, você precisa abrir explicitamente o que quer."),
                q("Em SG, posso permitir tráfego vindo de outro SG?",
                  "Sim, referenciando o SG-id no source.",
                  ["Só é possível autorizando pelo lado do IAM, não pelo SG.",
                   "Não, cada Security Group só enxerga tráfego por IP fixo.",
                   "Restrito só a tráfego IPv6, sem aceitar referência de outro SG."],
                  "Encadeamento por SG é a melhor prática para evitar IP hardcoded."),
                q("NACL avalia regras:",
                  "Em ordem numérica até encontrar match.",
                  ["Considera só a última regra cadastrada, ignorando as anteriores.",
                   "De forma aleatória, sem ordem definida entre as regras existentes.",
                   "Baseado no timestamp de criação de cada regra individual."],
                  "Por isso convenciona-se números (100, 200, 300...) e regra final 32766/deny all."),
                q("Para HTTPS, qual porta liberar?",
                  "443 TCP.",
                  ["8443 TCP, uma porta alternativa às vezes usada por proxy.",
                   "443 UDP, usado por QUIC/HTTP-3, não pelo HTTPS clássico.",
                   "80 UDP, uma combinação que não corresponde a um uso comum na prática."],
                  "443 TCP é o padrão; HTTP/3 usa 443 UDP, mas só libere se a app for HTTP/3."),
                q("SG aplica-se a:",
                  "Interfaces de rede (ENIs).",
                  ["Subnet inteira, aplicando a mesma regra a cada IP dentro dela.",
                   "Só ao protocolo IPv6, sem cobertura para tráfego IPv4.",
                   "Só a função Lambda, sem aplicar a outro tipo de recurso."],
                  "ENI pode ter até 5 SGs (limite ajustável). Lambda em VPC também usa SG da ENI."),
                q("Boas práticas com SG:",
                  "Granularidade alta, sem 0.0.0.0/0 desnecessário.",
                  ["Abrir 0.0.0.0/0 de entrada em qualquer porta disponível do servidor.",
                   "Deixar de atualizar a regra por meses, mesmo com mudança de escopo.",
                   "Usar o mesmo Security Group compartilhado pela infraestrutura inteira."],
                  "Granular = mais regras, mas auditável e principle of least access."),
                q("Permitir 0.0.0.0/0 em SSH é:",
                  "Risco crítico de força bruta.",
                  ["Uma boa prática recomendada para ambiente de produção real.",
                   "Bloqueia completamente o serviço sshd assim que aplicado.",
                   "Necessário para o protocolo SSH funcionar de alguma forma."],
                  "Use bastion, VPN ou SSM Session Manager. SSH público em produção = manchete esperando acontecer."),
                q("Como auditar uso de SG?",
                  "VPC Flow Logs e CloudTrail.",
                  ["Não é possível auditar esse tipo de mudança de forma alguma disponível hoje.",
                   "Rodar o comando top dentro do próprio servidor monitorado.",
                   "Consultar só o histórico de resolução de nome feito via DNS."],
                  "Flow Logs mostra tráfego; CloudTrail mostra mudanças nas regras."),
            ],
        },
        # =====================================================================
        # 2.6 Object Storage (S3)
        # =====================================================================
        {
            "title": "Object Storage (S3)",
            "summary": "Armazenamento de arquivos e permissões de acesso público/privado.",
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
            },
            "materials": [
                m("AWS S3 User Guide",
                  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
                  "docs", ""),
                m("Azure Blob Storage",
                  "https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview",
                  "docs", ""),
                m("GCS docs", "https://cloud.google.com/storage/docs", "docs", ""),
                m("AWS S3 Block Public Access",
                  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html",
                  "docs", ""),
                m("MinIO (S3 compat)",
                  "https://min.io/docs/minio/linux/index.html", "docs", ""),
                m("AWS Macie (descobre PII)",
                  "https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html",
                  "docs", ""),
            ],
            "questions": [
                q("Bucket público sem necessidade leva a:",
                  "Vazamento de dados.",
                  ["Performance maior de leitura, já que qualquer um pode acessar direto.",
                   "Backup automático feito pelo próprio provedor sem custo adicional.",
                   "Auto-scaling de capacidade de armazenamento conforme demanda cresce."],
                  "Maior parte dos vazamentos cloud nas últimas duas décadas começou em S3 público."),
                q("Presigned URL serve para:",
                  "Conceder acesso temporário a um objeto sem expor credenciais.",
                  ["Substitui completamente a necessidade de configurar IAM no bucket.",
                   "Renomear arquivo em lote dentro de um bucket já existente.",
                   "Acelerar o upload de arquivo grande usando conexão paralela."],
                  "TTL curto reduz risco. Limite método e tamanho para minimizar abuso."),
                q("Versionamento em S3 ajuda em:",
                  "Recuperação após exclusão acidental ou ransomware.",
                  ["Backup financeiro exigido por auditoria contábil da empresa.",
                   "Aumento real do número de IOPS disponível para o bucket.",
                   "Compressão automática aplicada a cada objeto armazenado."],
                  "Combine com MFA Delete e Object Lock para defesa em camadas."),
                q("SSE-KMS criptografa:",
                  "Objetos em repouso usando chaves do KMS.",
                  ["Só o nome do arquivo, sem tocar no conteúdo real do objeto.",
                   "Só a tag associada ao objeto, sem cifrar o conteúdo dele.",
                   "O tráfego em trânsito entre cliente e servidor, via TLS."],
                  "Trânsito é coberto por TLS (HTTPS). KMS adiciona granularidade, você pode "
                  "controlar quem usa cada chave."),
                q("'Block Public Access' na conta:",
                  "Garante que nenhum bucket fique exposto por engano.",
                  ["Aumenta o custo mensal cobrado pelo armazenamento no S3.",
                   "Apaga objeto já existente dentro de qualquer bucket da conta.",
                   "Bloqueia a criação de política nova dentro do IAM da conta."],
                  "Quatro flags; ative as quatro a menos que tenha caso justificável de bucket público."),
                q("Lifecycle rule pode:",
                  "Mover objetos a Glacier após N dias.",
                  ["Habilita o protocolo HTTPS para as requisições feitas ao bucket.",
                   "Renomeia o bucket inteiro sem precisar recriar o conteúdo.",
                   "Substitui a política de IAM aplicada ao bucket inteiro."],
                  "Reduz custo drasticamente para dados frios. Cuidado com custo de retrieval em Glacier."),
                q("Para hospedar site estático em S3:",
                  "Habilite static website hosting + use CloudFront na frente.",
                  ["Use Route53 isoladamente, sem qualquer outro serviço envolvido no caminho.",
                   "Use Lambda como servidor web, processando cada requisição HTTP recebida.",
                   "Use EC2 dedicada, mantendo o servidor ligado continuamente de forma manual."],
                  "CloudFront + Origin Access Identity permite manter o bucket privado."),
                q("Logs de acesso ao bucket vão para:",
                  "Outro bucket configurado como destino.",
                  ["O CloudWatch sozinho, sem exigir bucket adicional para isso.",
                   "O console da AWS, mostrado direto na tela, sem persistir em lugar algum.",
                   "Um destino que não existe, já que o S3 não gera esse log sozinho."],
                  "Bucket de logs deve ser separado e com policy restritiva. Considere também CloudTrail data events."),
                q("Como evitar deleção acidental?",
                  "Object Lock + versionamento + MFA Delete.",
                  ["Só a policy do IAM aplicada à conta, sem qualquer outra camada configurada.",
                   "Um backup guardado localmente, fora da infraestrutura da AWS.",
                   "Não criar arquivo novo, mantendo o bucket permanentemente vazio."],
                  "Object Lock em modo Compliance impede até root de apagar antes do TTL."),
                q("S3 tem garantia de durabilidade nominal de:",
                  "11 noves (99.999999999%).",
                  ["3 noves (99.9%), padrão comum em serviço menos crítico.",
                   "5 noves (99.999%), acima do S3 Standard em disponibilidade.",
                   "Sem garantia formal de durabilidade documentada pelo provedor."],
                  "Calculado replicando objetos cross-AZ. Disponibilidade é menor (4 noves no Standard)."),
            ],
        },
        # =====================================================================
        # 2.7 Criptografia em Repouso e Trânsito
        # =====================================================================
        {
            "title": "Criptografia em Repouso e Trânsito",
            "summary": "Proteção de dados com chaves KMS e TLS/SSL.",
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
            },
            "materials": [
                m("AWS KMS",
                  "https://docs.aws.amazon.com/kms/latest/developerguide/", "docs", ""),
                m("Azure Key Vault",
                  "https://learn.microsoft.com/azure/key-vault/general/overview", "docs", ""),
                m("GCP Cloud KMS",
                  "https://cloud.google.com/kms/docs", "docs", ""),
                m("Mozilla TLS Guidelines",
                  "https://wiki.mozilla.org/Security/Server_Side_TLS", "docs", ""),
                m("Cloudflare: SSL/TLS",
                  "https://www.cloudflare.com/learning/ssl/transport-layer-security-tls/",
                  "article", ""),
                m("OWASP Cryptographic Storage Cheatsheet",
                  "https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html",
                  "docs", ""),
            ],
            "questions": [
                q("AES-256 é simétrica ou assimétrica?",
                  "Simétrica.",
                  ["Assimétrica.", "Sem chave.", "Quântica."],
                  "Mesma chave cifra/decifra. Por isso a chave nunca pode vazar."),
                q("TLS depende de:",
                  "Certificado X.509 e chave privada.",
                  ["Só o endereço IP do servidor, sem verificação de identidade.",
                   "Só a regra de firewall liberando a porta 443, sem certificado.",
                   "Só a resolução de nome feita pelo DNS antes da conexão."],
                  "Cliente verifica o certificado contra CAs confiáveis; servidor prova posse da chave privada."),
                q("Por que rotacionar chaves KMS?",
                  "Reduz impacto de eventual comprometimento.",
                  ["Um requisito real do protocolo HTTP sem criptografia.",
                   "Reduz o custo mensal cobrado pelo uso do serviço de chave.",
                   "Aumenta a velocidade de resposta da chamada de API feita."],
                  "KMS rotaciona automaticamente em CMKs gerenciadas (anual). Re-criptografa lazy ao acessar."),
                q("HSM serve para:",
                  "Armazenar chaves criptográficas em hardware dedicado.",
                  ["Criar política de acesso dentro do IAM da própria conta AWS.",
                   "Substituir por completo a necessidade de configurar IAM na conta.",
                   "Comprimir o dado antes de armazená-lo fisicamente em disco."],
                  "HSMs têm certificações (FIPS 140-3 Level 3) e impedem extração da chave."),
                q("Algoritmo recomendado para hash de senha:",
                  "Argon2 ou bcrypt com custo alto.",
                  ["SHA-1, hash rápido demais e já quebrado por colisão.",
                   "Base64, só uma codificação reversível, não um hash de verdade.",
                   "MD5, hash antigo e vulnerável a ataque de força bruta rápido."],
                  "Argon2 ganhou a Password Hashing Competition. bcrypt continua aceitável."),
                q("Forward secrecy garante:",
                  "Que comprometimento da chave atual não revele tráfego antigo.",
                  ["Uma velocidade de handshake maior do que a versão anterior do protocolo.",
                   "Um backup automático da chave de sessão usada na conexão.",
                   "Compatibilidade retroativa com o antigo e inseguro SSLv2."],
                  "ECDHE gera chave de sessão efêmera. Sem forward secrecy, atacante guarda tráfego "
                  "para descriptografar quando obtiver a chave."),
                q("HSTS é mecanismo de:",
                  "Força HTTPS em browsers.",
                  ["Roteamento de pacote entre duas redes distintas.",
                   "Backup periódico do certificado emitido pela CA.",
                   "Criptografia de dado parado em disco, não em trânsito."],
                  "Header HTTP que diz: 'sempre acesse este host por HTTPS pelos próximos N segundos'."),
                q("Certificate Authority (CA) confiável é necessária para:",
                  "Que clientes confiem no certificado sem warning.",
                  ["Aumentar a performance de resposta do servidor web.",
                   "Servir conteúdo em HTTP puro, sem qualquer camada de TLS envolvida.",
                   "Comprimir dado antes de enviar pela rede ao cliente."],
                  "Em produção pública use Let's Encrypt/ACM/etc. Em interno, considere CA privada (Vault, AWS PCA)."),
                q("Vazou a chave privada do TLS, deve-se:",
                  "Revogar e rotacionar imediatamente.",
                  ["Manter em uso por compatibilidade com cliente antigo.",
                   "Abrir um chamado de SLA com o provedor de certificado.",
                   "Apagar log antigo relacionado ao uso daquela chave."],
                  "Tráfego antigo pode ser descriptografado se não houver forward secrecy. Revogue via CRL/OCSP."),
                q("'Encryption at rest' protege:",
                  "Dados armazenados em disco.",
                  ["Só o dado que está temporariamente na memória RAM.",
                   "Só a resolução de nome feita pelo servidor de DNS.",
                   "Tráfego trafegando entre dois servidores diferentes."],
                  "Mitiga roubo de disco/snapshot. Não protege se atacante já tem acesso lógico ao recurso."),
            ],
        },
        # =====================================================================
        # 2.8 Monitoramento Básico
        # =====================================================================
        {
            "title": "Monitoramento Básico (CloudWatch/Monitor)",
            "summary": "Saber se o servidor está vivo e saudável.",
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
                "body": (
                    "<h3>1. Os 4 sinais de ouro (Google SRE)</h3>"
                    "<p>De todas as métricas que você pode coletar, 4 dizem se um serviço "
                    "está bem ou mal:</p>"
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
            },
            "materials": [
                m("Google SRE: SLO, SLI, SLA",
                  "https://sre.google/sre-book/service-level-objectives/", "book", ""),
                m("AWS CloudWatch",
                  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
                  "docs", ""),
                m("Azure Monitor docs",
                  "https://learn.microsoft.com/azure/azure-monitor/overview", "docs", ""),
                m("Prometheus",
                  "https://prometheus.io/docs/introduction/overview/", "docs", ""),
                m("Grafana docs",
                  "https://grafana.com/docs/grafana/latest/", "docs", ""),
                m("OpenTelemetry",
                  "https://opentelemetry.io/docs/", "docs",
                  "Padrão para instrumentação."),
            ],
            "questions": [
                q("Os '4 golden signals' são:",
                  "Latência, tráfego, erros e saturação.",
                  ["CPU, RAM, disco e rede, métricas de infraestrutura básica.",
                   "Requisição por segundo, quadro por segundo, megabyte, milissegundo.",
                   "Estado de ligado ou desligado, sem qualquer outra dimensão medida."],
                  "Definidos pelo Google SRE Book. Cobrem as dimensões essenciais de qualquer serviço."),
                q("SLO mede:",
                  "Objetivo de qualidade de serviço (ex.: 99,9% de disponibilidade).",
                  ["Custo mensal total cobrado pela conta de cloud usada pela aplicação inteira.",
                   "Contagem total de bug reportado no rastreador de issue usado pelo time inteiro.",
                   "Latência de uma única requisição específica, medida em um único momento isolado."],
                  "É o objetivo interno; SLA é o contrato com cliente (geralmente mais conservador)."),
                q("Diferença SLI vs SLO:",
                  "SLI é a medida (indicador), SLO é o objetivo.",
                  ["São a mesma coisa, só com nome diferente entre ferramenta.",
                   "O SLO é a métrica bruta coletada direto do sistema monitorado.",
                   "O SLI é o contrato formal assinado diretamente com o cliente."],
                  "Você mede SLI; SLO é o limite que diz se está bom ou ruim."),
                q("Por que alarme em SLO em vez de threshold:",
                  "Refletem o que importa para o usuário, não números arbitrários.",
                  ["Substituem completamente a necessidade de manter log estruturado.",
                   "Reduzem o custo mensal pago pela ferramenta de observabilidade.",
                   "Habilitam o protocolo HTTPS na camada de balanceamento de carga."],
                  "Burn rate alerta quando o orçamento de erro está sendo consumido rápido, sinal real, não ruído."),
                q("PromQL é linguagem de:",
                  "Consulta do Prometheus.",
                  ["JSON, formato de dado usado para troca entre sistema.",
                   "Python usado para escrever a lógica interna de um alarme.",
                   "Formato de log estruturado usado por ferramenta de observabilidade."],
                  "Permite agregações, taxas (`rate(...)[5m]`), percentis (`histogram_quantile`)."),
                q("Histograma em métricas serve para:",
                  "Distribuir valores em buckets e calcular percentis (p99 etc.).",
                  ["Substituir completamente o uso de trace distribuído na aplicação.",
                   "Contar requisição recebida, sem cálculo estatístico adicional envolvido.",
                   "Listar cada erro individualmente, sem qualquer agregação aplicada ao resultado."],
                  "Histograma é local (cliente). Para somar entre instâncias, use buckets compatíveis."),
                q("Alert fadiga ocorre quando:",
                  "Há tantos alertas que ninguém presta atenção.",
                  ["O Prometheus cai e para de coletar métrica nova.",
                   "O SLA contratado aumenta além do que era esperado.",
                   "O Grafana atualiza a versão do dashboard automaticamente."],
                  "Cada alerta sem ação útil corrói a confiança no sistema. Limpe agressivamente."),
                q("Métrica vs log vs trace:",
                  "Métrica é numérica agregada; log é evento; trace é fluxo distribuído.",
                  ["São a mesma coisa, só chamada de forma diferente por cada time de engenharia.",
                   "Só o trace importa de verdade, os outros dois são completamente dispensáveis.",
                   "Métrica e trace são exatamente o mesmo conceito, só com nome trocado entre time diferente."],
                  "Os três são pilares da observabilidade, complementares, não substitutos."),
                q("SLO de 99,99% permite quantos minutos de downtime/mês?",
                  "Cerca de 4,3 minutos.",
                  ["Cerca de 1 hora inteira de indisponibilidade tolerada por mês.",
                   "0 minutos, já que 99,99% exigiria disponibilidade completa o tempo inteiro.",
                   "Cerca de 1 dia inteiro de indisponibilidade tolerada por mês."],
                  "30d x 24h x 60min x 0,01% ≈ 4,3 min. Quatro noves é caro."),
                q("Cardinalidade alta em métricas causa:",
                  "Custo crescente e degradação do backend.",
                  ["Auto-resolução do problema sem intervenção humana necessária.",
                   "Backup automático do dado coletado pela ferramenta de métrica.",
                   "Aceleração real da consulta feita contra o banco de métrica."],
                  "Cada combinação única de labels é uma série. Evite user_id/request_id em métricas."),
            ],
        },
        # =====================================================================
        # 2.9 Backup & DR
        # =====================================================================
        {
            "title": "Backup & Disaster Recovery",
            "summary": "Como não perder tudo em caso de falha.",
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
            },
            "materials": [
                m("AWS Backup",
                  "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html",
                  "docs", ""),
                m("Veeam: 3-2-1 backup rule",
                  "https://www.veeam.com/blog/321-backup-rule.html", "article", ""),
                m("Google: Disaster Recovery Planning",
                  "https://cloud.google.com/architecture/dr-scenarios-planning-guide",
                  "article", ""),
                m("Azure Site Recovery",
                  "https://learn.microsoft.com/azure/site-recovery/site-recovery-overview",
                  "docs", ""),
                m("Restic backup", "https://restic.readthedocs.io/", "tool",
                  "Open source, deduplicado, criptografado."),
                m("AWS Fault Injection Simulator",
                  "https://docs.aws.amazon.com/fis/latest/userguide/what-is.html",
                  "tool", "Game day on demand."),
            ],
            "questions": [
                q("RPO mede:",
                  "Quanto dado é aceitável perder em caso de incidente.",
                  ["Tempo até voltar.",
                   "Custo de cloud.",
                   "Velocidade do disco."],
                  "RPO baixo = backups frequentes. RPO=0 só com replicação síncrona, e cara."),
                q("RTO mede:",
                  "Tempo aceitável para retomar a operação.",
                  ["Quanto dado se perde.",
                   "Latência.",
                   "Throughput."],
                  "RTO baixo = automação. Atender RTO de minutos manualmente é impossível."),
                q("Regra 3-2-1 sugere:",
                  "3 cópias, em 2 mídias, com 1 offsite.",
                  ["3 réplicas no mesmo disco.",
                   "1 cópia local apenas.",
                   "Backup só semanal."],
                  "Sobrevive a incêndio do datacenter, ransomware na conta principal e mídia falha."),
                q("Snapshot incremental:",
                  "Salva só as mudanças desde o último snapshot.",
                  ["Salva tudo de novo.",
                   "Apaga snapshots antigos.",
                   "Substitui o backup full."],
                  "Eficiente em espaço, mas restore depende da cadeia de incrementais."),
                q("Backup sem teste é:",
                  "Inútil, só descobre o problema na hora.",
                  ["Suficiente.",
                   "Garantia legal.",
                   "Sempre rápido."],
                  "Game day mensal/trimestral revela schemas que mudaram, credenciais que expiraram, etc."),
                q("DR em região alternativa serve para:",
                  "Mitigar falha de uma região inteira.",
                  ["Reduzir latência local.",
                   "Aumentar custo.",
                   "Trocar de cloud."],
                  "Region failures são raros mas existem (us-east-1 outages)."),
                q("Encriptação de backup é:",
                  "Obrigatória, backup vaza, dado vaza.",
                  ["Opcional.",
                   "Inútil.",
                   "Só para banco."],
                  "Backup é onde quase todo dado está, junto. KMS + bucket policy restritiva."),
                q("Game day em DR é:",
                  "Simulação real para validar runbooks.",
                  ["Festa do time.",
                   "Hackathon.",
                   "Auditoria fiscal."],
                  "Documente lições aprendidas e ajuste runbook após cada game day."),
                q("Pilot light é:",
                  "Estratégia DR com infraestrutura mínima ativa em outra região.",
                  ["Cron.",
                   "Modo de IAM.",
                   "Tipo de S3."],
                  "Equilibra custo (baixo) com RTO razoável (minutos), comparado a backup-restore (horas)."),
                q("Cold backup vs hot backup:",
                  "Cold é com app parado; hot é com app rodando (consistente).",
                  ["São idênticos.",
                   "Hot é mais simples.",
                   "Cold é online."],
                  "Hot exige consistência transacional (ex.: snapshot WAL do Postgres)."),
            ],
        },
        # =====================================================================
        # 2.10 FinOps
        # =====================================================================
        {
            "title": "FinOps Inicial",
            "summary": "Evitar surpresas na fatura do cartão de crédito no fim do mês.",
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
            },
            "materials": [
                m("FinOps Foundation", "https://www.finops.org/", "article", ""),
                m("AWS Cost Optimization",
                  "https://aws.amazon.com/aws-cost-management/", "docs", ""),
                m("Azure Cost Management",
                  "https://learn.microsoft.com/azure/cost-management-billing/cost-management-billing-overview",
                  "docs", ""),
                m("GCP cost optimization",
                  "https://cloud.google.com/architecture/framework/cost-optimization",
                  "docs", ""),
                m("Komiser (OSS)", "https://github.com/tailwarden/komiser",
                  "tool", ""),
                m("Cloud Custodian",
                  "https://cloudcustodian.io/", "tool",
                  "Policies as code para limpeza automatizada."),
            ],
            "questions": [
                q("Tag obrigatória recomendada:",
                  "Owner, Environment, CostCenter.",
                  ["Apenas Name.",
                   "Apenas Region.",
                   "Apenas Type."],
                  "Sem tags consistentes, atribuição de custo vira política em vez de matemática."),
                q("Spot Instance é:",
                  "VM barata que pode ser interrompida.",
                  ["VM premium.",
                   "Disco SSD.",
                   "Tipo de IAM."],
                  "Aviso de 2 minutos antes da interrupção. Ideal para batch, CI, treino de ML."),
                q("Reserved Instance dá desconto se:",
                  "Você se compromete por 1 ou 3 anos.",
                  ["Pagar antecipado para sempre.",
                   "Usar IPv6.",
                   "Não usar nada."],
                  "Savings Plans são mais flexíveis (qualquer family/region) com desconto similar."),
                q("Recurso órfão é:",
                  "Recurso sem uso que ainda é cobrado (ex.: snapshot antigo).",
                  ["Recurso sem dono no IAM.",
                   "Recurso com erro.",
                   "Recurso de teste."],
                  "Use Cloud Custodian para detectar e remediar (ex.: deletar snapshots > 90d)."),
                q("Right-sizing é:",
                  "Ajustar tamanho de instâncias ao uso real.",
                  ["Tamanho mínimo sempre.",
                   "Tamanho máximo sempre.",
                   "Apenas largura de disco."],
                  "Ferramentas mostram CPU/memória médio e sugerem família/tamanho menor."),
                q("Budget alerts servem para:",
                  "Avisar antes do orçamento estourar.",
                  ["Acelerar deploy.",
                   "Reduzir latência.",
                   "Aumentar quota automaticamente."],
                  "Configure alertas em 50%/80%/100% para evitar surpresa no fim do mês."),
                q("FinOps maturity vai do crawl ao:",
                  "Run.",
                  ["Sprint.",
                   "Spawn.",
                   "Stop."],
                  "Crawl (visibilidade) → Walk (otimização contínua) → Run (decisões de produto)."),
                q("Para batches diários:",
                  "Considere Spot/Preemptible.",
                  ["On-demand sempre.",
                   "Reserved 3 anos.",
                   "Local hardware."],
                  "Batch tolera interrupção; spot economiza até 90% comparado a on-demand."),
                q("Auto Scaling reduz custo porque:",
                  "Provisiona apenas quando há demanda.",
                  ["Aumenta quota.",
                   "Subtitui IAM.",
                   "Libera segurança."],
                  "Combine com warm pool para reduzir cold start e ainda economizar."),
                q("Showback vs chargeback:",
                  "Showback mostra; chargeback cobra internamente.",
                  ["São sinônimos.",
                   "Ambos cobram clientes externos.",
                   "Não existem."],
                  "Showback gera consciência. Chargeback cria accountability, recomendado em "
                  "estágios mais maduros de FinOps."),
            ],
        },
    ],
}
