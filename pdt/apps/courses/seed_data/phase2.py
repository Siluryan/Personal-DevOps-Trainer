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
                    "<h3>1. Da máquina física à VM: hypervisor</h3>"
                    "<p>Antes de cloud havia datacenter com servidores físicos. Cada workload "
                    "ocupava uma máquina inteira; utilização típica girava em torno de 10-15%. "
                    "<strong>Hypervisor</strong> é o software que cria múltiplas máquinas "
                    "virtuais sobre o mesmo hardware:</p>"
                    "<ul>"
                    "<li><strong>Tipo 1 (bare-metal)</strong>: roda direto no hardware, com "
                    "acesso privilegiado às extensões de virtualização da CPU "
                    "(Intel VT-x, AMD-V). Exemplos: <strong>KVM</strong> (Linux), VMware ESXi, "
                    "Microsoft Hyper-V, Xen, AWS Nitro Hypervisor (forquilha custom de KVM). "
                    "<em>É o que cloud pública usa.</em></li>"
                    "<li><strong>Tipo 2 (hosted)</strong>: roda como aplicação dentro de um SO "
                    "convencional. Exemplos: VirtualBox, VMware Workstation, Parallels. Útil "
                    "em desktop, ineficiente em servidor.</li>"
                    "</ul>"
                    "<p>Cada VM tem kernel próprio, drivers virtualizados (paravirtualização: "
                    "<code>virtio</code>), endereço IP próprio. Você pode rodar Windows, Linux "
                    "e BSD lado a lado no mesmo host físico.</p>"

                    "<h3>2. Container ≠ VM</h3>"
                    "<p>Comparação direta:</p>"
                    "<table>"
                    "<tr><th></th><th>VM</th><th>Container</th></tr>"
                    "<tr><td>Kernel</td><td>próprio</td><td>compartilhado com host</td></tr>"
                    "<tr><td>Boot</td><td>segundos a minutos</td><td>milissegundos</td></tr>"
                    "<tr><td>Tamanho</td><td>GBs</td><td>dezenas a centenas de MB</td></tr>"
                    "<tr><td>Isolamento</td><td>forte (boundary do hypervisor)</td>"
                    "<td>processo (namespaces + cgroups + seccomp)</td></tr>"
                    "<tr><td>SO no guest</td><td>qualquer</td><td>mesmo kernel do host</td></tr>"
                    "</table>"
                    "<p>Containers são processos isolados, não máquinas. Em Linux usam:</p>"
                    "<ul>"
                    "<li><strong>Namespaces</strong>: isolam visão de PID, mount, rede, IPC, "
                    "user, UTS. Cada container 'vê' só o seu mundo.</li>"
                    "<li><strong>cgroups</strong>: limitam recursos (CPU, RAM, IO).</li>"
                    "<li><strong>seccomp / AppArmor / SELinux</strong>: restringem syscalls "
                    "que o container pode chamar.</li>"
                    "</ul>"
                    "<p>Para isolamento mais forte que container puro mas mais leve que VM "
                    "completa, <strong>microVMs</strong> (Firecracker da AWS, Kata Containers) "
                    "rodam um kernel mínimo dentro de KVM em centenas de ms.</p>"

                    "<h3>3. O que cloud adiciona sobre virtualização</h3>"
                    "<ul>"
                    "<li><strong>API everywhere</strong>: provisionar VM, rede, storage, banco "
                    "via chamada HTTP autenticada. Em VMware tradicional você abre ticket; em "
                    "AWS você roda <code>aws ec2 run-instances</code>.</li>"
                    "<li><strong>Pay-as-you-go</strong>: cobrança por hora, segundo, milissegundo "
                    "(Lambda) ou byte (S3). Capex vira opex.</li>"
                    "<li><strong>Multi-tenancy</strong>: muitos clientes na mesma infra "
                    "física, isolados por software.</li>"
                    "<li><strong>Serviços gerenciados</strong>: RDS, Cloud SQL, DynamoDB, "
                    "EKS, você paga uma camada acima da VM.</li>"
                    "<li><strong>Geo-distribuição</strong>: dezenas de regiões, dezenas de "
                    "AZs por região, edges em todo o mundo.</li>"
                    "<li><strong>Composição via IaC</strong>: Terraform, CloudFormation, "
                    "Pulumi descrevem infra inteira em texto versionado.</li>"
                    "</ul>"

                    "<h3>4. IaaS vs PaaS vs SaaS, o trade-off de controle</h3>"
                    "<p>A diferença é <em>quem opera o quê</em>:</p>"
                    "<table>"
                    "<tr><th></th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>"
                    "<tr><td>Você controla</td><td>SO, runtime, app, dados</td>"
                    "<td>app, dados</td><td>config, dados</td></tr>"
                    "<tr><td>Provedor controla</td><td>hardware, hypervisor</td>"
                    "<td>hardware, hypervisor, SO, runtime</td><td>tudo</td></tr>"
                    "<tr><td>Exemplos</td><td>EC2, GCE, Azure VM</td>"
                    "<td>App Engine, Heroku, Cloud Run, App Service</td>"
                    "<td>Gmail, Notion, GitHub, Salesforce</td></tr>"
                    "<tr><td>Esforço operacional</td><td>alto</td><td>médio</td><td>quase zero</td></tr>"
                    "<tr><td>Lock-in</td><td>baixo</td><td>alto</td><td>muito alto</td></tr>"
                    "<tr><td>Granularidade</td><td>total</td><td>limitada</td><td>nenhuma</td></tr>"
                    "</table>"
                    "<p>Tendências recentes: <strong>serverless</strong> (Lambda, Cloud "
                    "Functions, Cloud Run) e <strong>containers as a service</strong> (Fargate, "
                    "Cloud Run) ficam entre PaaS e IaaS, você entrega uma imagem ou função, "
                    "provedor cuida do resto.</p>"

                    "<h3>5. Anatomia de uma região AWS (e equivalentes)</h3>"
                    "<pre><code>Region (ex.: us-east-1, sa-east-1, eu-west-3)\n"
                    "├── AZ a (datacenter A)        ← latência ~1-2ms intra-AZ\n"
                    "├── AZ b (datacenter B)        ← latência ~1-2ms intra-AZ\n"
                    "└── AZ c (datacenter C)        ← latência ~1-2ms entre-AZ\n"
                    "    │\n"
                    "    └── Edges (POPs / CloudFront / Global Accelerator)\n"
                    "         espalhados por dezenas de cidades</code></pre>"
                    "<p>Termos:</p>"
                    "<ul>"
                    "<li><strong>Region</strong>: conjunto de datacenters em uma localidade "
                    "geográfica (us-east-1 = Northern Virginia).</li>"
                    "<li><strong>Availability Zone (AZ)</strong>: um ou mais datacenters "
                    "isolados, diferentes power, cooling, network. Falha de uma AZ não "
                    "afeta as outras (em tese).</li>"
                    "<li><strong>Edge / POP</strong>: ponto de presença para CDN e "
                    "aceleração, não roda toda a sua app, mas cacheia conteúdo perto do "
                    "usuário.</li>"
                    "</ul>"
                    "<p>HA básico = multi-AZ. HA serious = multi-region (com replicação "
                    "ativa-ativa ou ativa-passiva). Multi-region é caro e complexo, ative só "
                    "se SLA exigir.</p>"

                    "<h3>6. Os 'Big 3' e os outros</h3>"
                    "<table>"
                    "<tr><th></th><th>AWS</th><th>Azure</th><th>GCP</th></tr>"
                    "<tr><td>Computação</td><td>EC2</td><td>VM</td><td>Compute Engine</td></tr>"
                    "<tr><td>Container managed</td><td>EKS / Fargate</td>"
                    "<td>AKS / Container Apps</td><td>GKE / Cloud Run</td></tr>"
                    "<tr><td>Object Storage</td><td>S3</td><td>Blob Storage</td><td>GCS</td></tr>"
                    "<tr><td>SQL gerenciado</td><td>RDS</td><td>Azure SQL / DB</td>"
                    "<td>Cloud SQL / AlloyDB</td></tr>"
                    "<tr><td>NoSQL</td><td>DynamoDB</td><td>Cosmos DB</td><td>Bigtable / Firestore</td></tr>"
                    "<tr><td>Serverless function</td><td>Lambda</td>"
                    "<td>Functions</td><td>Cloud Functions / Run</td></tr>"
                    "<tr><td>Identidade</td><td>IAM</td><td>Entra ID</td><td>IAM</td></tr>"
                    "<tr><td>Rede</td><td>VPC</td><td>VNet</td><td>VPC</td></tr>"
                    "</table>"
                    "<p>Alternativas relevantes: DigitalOcean (developer-friendly), Linode/"
                    "Akamai, Hetzner (preço imbatível na Europa), Oracle Cloud (free tier "
                    "generoso), Cloudflare (edge-first), Fly.io (deploy de containers "
                    "globalmente).</p>"

                    "<h3>7. Tipos de cloud: pública, privada, híbrida, edge</h3>"
                    "<ul>"
                    "<li><strong>Pública</strong>: AWS/Azure/GCP. Compartilhada. Maior "
                    "elasticidade, melhor preço por TB.</li>"
                    "<li><strong>Privada</strong>: datacenter próprio com VMware/OpenStack, ou "
                    "VPC/dedicated em provedor. Isolamento legal/regulatório, mas perde "
                    "elasticidade.</li>"
                    "<li><strong>Híbrida</strong>: combina ambos via VPN/Direct Connect/ "
                    "Outposts. Útil em transição ou para dados que <em>não podem</em> sair "
                    "(LGPD, soberania).</li>"
                    "<li><strong>Edge</strong>: computação perto do usuário final. "
                    "Cloudflare Workers, AWS Lambda@Edge, Fastly Compute@Edge. Latência de "
                    "&lt;50ms globalmente.</li>"
                    "<li><strong>Multi-cloud</strong>: vários provedores simultaneamente. "
                    "Hype passou; complexidade real é alta.</li>"
                    "</ul>"

                    "<h3>8. Trade-offs reais que ninguém explica no marketing</h3>"
                    "<ul>"
                    "<li><strong>Egress é caro</strong>: AWS cobra ~9¢/GB para tráfego saindo. "
                    "Aplicação que serve muito vídeo paga uma fortuna. Cloudflare R2 e "
                    "alternativas zeram egress como diferencial.</li>"
                    "<li><strong>Lock-in é real</strong>: usar DynamoDB ou BigQuery 'até o "
                    "fim' significa que migrar é projeto de meses. Avalie 'como saio?' antes "
                    "de adotar serviço gerenciado proprietário.</li>"
                    "<li><strong>Falhas existem</strong>: us-east-1 já caiu por horas várias "
                    "vezes (2017, 2021, 2023). Multi-region não é luxo em sistemas "
                    "críticos.</li>"
                    "<li><strong>Latência da AZ-distante</strong>: ~1-2ms intra-AZ vs "
                    "~10-100ms cross-region. Banco de dados pode degradar.</li>"
                    "<li><strong>FinOps fica caro</strong>: depois de 6 meses, contas com "
                    "milhares de recursos órfãos viram normal sem disciplina.</li>"
                    "</ul>"

                    "<h3>9. Caso real: o jornalista que ganhou um datacenter</h3>"
                    "<p>Em 2017, um jornalista holandês colocou seu site novo na AWS "
                    "(s3+CloudFront). Hospedagem custaria ~US$ 5/mês para uns 10k "
                    "visitantes/dia. Ele esqueceu o write em DynamoDB sem rate-limit, e um "
                    "bug em loop fez milhões de writes por minuto. Em 24h: US$ 14k de fatura. "
                    "Lições: configure budgets/alertas <em>antes</em> do primeiro deploy, "
                    "rate-limit em <em>tudo</em>, soft-delete em vez de write-loop.</p>"

                    "<h3>10. Quando cloud não é a resposta</h3>"
                    "<p>Casos onde on-prem ainda ganha:</p>"
                    "<ul>"
                    "<li>Workload de utilização constante e previsível (DB sempre cheio): "
                    "hardware comprado uma vez é mais barato em 3 anos.</li>"
                    "<li>Dados que não podem sair do país (algumas regulações).</li>"
                    "<li>Latência ultra-baixa (HFT trading).</li>"
                    "<li>Cargas com I/O massivo de armazenamento (cloud cobra caro por "
                    "IOPS).</li>"
                    "</ul>"
                    "<p>Para tudo o resto, startup nova, app web típica, batch ML, "
                    "site/blog, cloud é geralmente a escolha óbvia.</p>"
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
                  ["Roda dentro de outro SO.",
                   "É um tipo de container.",
                   "Substitui o BIOS."],
                  "Tipo 1 = bare-metal (KVM, ESXi, Hyper-V). Tipo 2 = roda como app dentro de "
                  "outro SO (VirtualBox)."),
                q("Cloud difere de virtualização porque:",
                  "Adiciona APIs, self-service e billing por uso.",
                  ["Não usa hardware.",
                   "Não tem rede.",
                   "Não suporta Linux."],
                  "Virtualização é fundação técnica; cloud junta automação, multi-tenancy e billing."),
                q("VM e container compartilham:",
                  "O hardware via virtualização (mesmo host físico).",
                  ["O mesmo kernel.",
                   "O mesmo hypervisor.",
                   "O mesmo IP."],
                  "Containers compartilham kernel; VMs têm kernel próprio. Ambos podem rodar no mesmo host."),
                q("Vantagem de cloud para startups:",
                  "Capex baixo e elasticidade.",
                  ["Hardware proprietário.",
                   "Sem necessidade de monitoramento.",
                   "Latência zero."],
                  "Pay-as-you-go evita compra de hardware para pico que pode nem existir."),
                q("Tipo de cloud onde recursos são exclusivos da empresa:",
                  "Private cloud.",
                  ["Public cloud.",
                   "Hybrid cloud.",
                   "Edge cloud."],
                  "Pode ser on-premise (datacenter próprio) ou VPC dedicada num provedor público."),
                q("Qual hypervisor é open source e parte do kernel Linux?",
                  "KVM",
                  ["VMware ESXi", "Hyper-V", "Xen Server proprietary"],
                  "KVM ('Kernel-based Virtual Machine') é módulo do kernel; libvirt e QEMU "
                  "completam o ecossistema."),
                q("'Pay-as-you-go' refere-se a:",
                  "Cobrar pelo uso real, sem compromisso de longo prazo.",
                  ["Pagar antecipado.",
                   "Pagar só se sucesso.",
                   "Não pagar."],
                  "Em muitos serviços (S3, Lambda, Run) você paga por requisição/byte. Em VMs, por hora/segundo."),
                q("Multi-tenancy implica:",
                  "Múltiplos clientes compartilhando infra com isolamento.",
                  ["Apenas um cliente por servidor.",
                   "Sem segregação.",
                   "Banco de dados único."],
                  "Isolamento via namespaces, IAM, redes virtuais. Provedor garante que tenant A não vê tenant B."),
                q("Region em cloud é:",
                  "Conjunto geográfico de datacenters (várias AZs).",
                  ["Uma máquina específica.",
                   "Um IP público.",
                   "Uma role de IAM."],
                  "Ex.: us-east-1 tem múltiplas AZs (us-east-1a, 1b, 1c). Latência baixa entre AZs, alta entre regiões."),
                q("Disponibilidade aumenta com:",
                  "Distribuir cargas entre múltiplas Availability Zones.",
                  ["Um único disco SSD.",
                   "Apenas backups.",
                   "Reduzir réplicas."],
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
                    "<h3>1. A linha móvel: quanto mais alto o serviço, mais o provedor cobre</h3>"
                    "<p>A divisão muda conforme o nível de abstração. Em geral:</p>"
                    "<table>"
                    "<tr><th>Camada</th><th>On-prem</th><th>IaaS</th><th>PaaS</th><th>SaaS</th></tr>"
                    "<tr><td>Datacenter, energia</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>"
                    "<tr><td>Rede física, hardware</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>"
                    "<tr><td>Hypervisor</td><td>você</td><td>provedor</td><td>provedor</td><td>provedor</td></tr>"
                    "<tr><td>SO, patches</td><td>você</td><td>VOCÊ</td><td>provedor</td><td>provedor</td></tr>"
                    "<tr><td>Runtime (libs, JVM, Python)</td><td>você</td><td>VOCÊ</td><td>provedor</td><td>provedor</td></tr>"
                    "<tr><td>Aplicação</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>provedor</td></tr>"
                    "<tr><td>Configuração de segurança</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>"
                    "<tr><td>Identidades, MFA</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>"
                    "<tr><td>Dados</td><td>você</td><td>VOCÊ</td><td>VOCÊ</td><td>VOCÊ</td></tr>"
                    "</table>"
                    "<p>Note como <strong>identidade, configuração e dados</strong> nunca "
                    "saem do cliente, em <em>nenhum</em> modelo. Esse é o ponto mais "
                    "importante.</p>"

                    "<h3>2. Os três grandes, visão oficial</h3>"
                    "<ul>"
                    "<li><strong>AWS</strong>: Security <em>OF</em> the Cloud (provedor) vs "
                    "Security <em>IN</em> the Cloud (você).</li>"
                    "<li><strong>Azure</strong>: 'Shared Responsibility' com matriz "
                    "específica por serviço.</li>"
                    "<li><strong>GCP</strong>: 'Shared Responsibility &amp; Shared Fate', "
                    "Google se compromete <em>ativamente</em> em ajudar você a fazer "
                    "certo, com defaults seguros.</li>"
                    "</ul>"
                    "<p>O modelo do GCP é mais novo e reconhece que 'jogar a responsabilidade "
                    "para o cliente' não basta, provedores precisam ser parceiros ativos "
                    "para reduzir misconfiguration.</p>"

                    "<h3>3. Caso a caso: o que muda por serviço</h3>"
                    "<p>Mesmo dentro do mesmo provedor, a divisão varia:</p>"
                    "<table>"
                    "<tr><th>Serviço</th><th>Você cuida de</th><th>Provedor cuida de</th></tr>"
                    "<tr><td>EC2 (IaaS)</td><td>SO, patches, app, dados, IAM, SG, dados</td>"
                    "<td>hypervisor, hardware, rede física</td></tr>"
                    "<tr><td>RDS (PaaS-DB)</td><td>schema, queries, backup config, IAM, "
                    "dados, encryption keys</td>"
                    "<td>SO, patches do MySQL/PG, replicação, HA, hardware</td></tr>"
                    "<tr><td>Lambda (FaaS)</td><td>código, deps, IAM, segredos, dados</td>"
                    "<td>SO, runtime, escala, hardware, isolamento</td></tr>"
                    "<tr><td>S3 (object storage)</td><td>policy, encryption keys, public access, "
                    "lifecycle, conteúdo dos objetos</td>"
                    "<td>durabilidade, hardware, encryption infra</td></tr>"
                    "<tr><td>EKS (managed K8s)</td><td>worker nodes, workloads, RBAC, network "
                    "policy, dados</td>"
                    "<td>control plane, etcd, upgrades do plane</td></tr>"
                    "<tr><td>M365 (SaaS)</td><td>identidades, compartilhamentos, retenção, "
                    "DLP, MFA</td>"
                    "<td>app, infra, disponibilidade</td></tr>"
                    "</table>"

                    "<h3>4. O que SEMPRE é seu, em qualquer serviço</h3>"
                    "<ol>"
                    "<li><strong>Identidades e acesso</strong>: usuários, roles, MFA, "
                    "policies. Mesmo no Gmail, sua MFA é problema seu.</li>"
                    "<li><strong>Classificação e proteção de dados</strong>: 'dado público "
                    "vs interno vs PII vs financeiro'. Mecanismos de DLP existem, mas "
                    "configurá-los é seu.</li>"
                    "<li><strong>Configuração de segurança</strong>: bucket público? SG "
                    "<code>0.0.0.0/0</code>? RDS sem encryption? Sempre seu.</li>"
                    "<li><strong>Backup configurável</strong>: retention, frequência, "
                    "cross-region. Defaults dos provedores são minimalistas.</li>"
                    "<li><strong>Logging e monitoring</strong>: CloudTrail, CloudWatch, "
                    "GuardDuty existem mas você precisa habilitá-los e mandar para um "
                    "lugar seguro.</li>"
                    "<li><strong>Compliance dos seus controles</strong>: o provedor "
                    "tem SOC 2 dele; você precisa do <em>seu</em>.</li>"
                    "</ol>"

                    "<h3>5. Misconfiguration é a causa #1, dados</h3>"
                    "<p>Verizon DBIR 2024: 31% das violações de cloud envolveram "
                    "<strong>misconfiguration</strong>. Gartner: 99% dos incidentes em cloud "
                    "até 2025 serão culpa do cliente.</p>"
                    "<p>Top misconfigurations recorrentes:</p>"
                    "<ul>"
                    "<li>S3 com leitura pública (Verizon, Accenture, Capital One, todos).</li>"
                    "<li>SG com SSH/RDP em <code>0.0.0.0/0</code>.</li>"
                    "<li>Conta root sem MFA.</li>"
                    "<li>Access keys hard-coded no GitHub público (~50k vazadas/ano).</li>"
                    "<li>RDS sem encryption at rest, sem backup configurado, sem snapshot "
                    "cross-region.</li>"
                    "<li>IAM com <code>AdministratorAccess</code> em apps.</li>"
                    "<li>Public IP em containers/funções 'só para teste' nunca removidos.</li>"
                    "<li>Logs (CloudTrail) desligados na conta.</li>"
                    "</ul>"

                    "<h3>6. Guard-rails: prevenir em vez de detectar</h3>"
                    "<p>Em vez de torcer para os times configurarem certo, configure "
                    "<strong>guard-rails</strong> que <em>impedem</em> configurações "
                    "inseguras:</p>"
                    "<ul>"
                    "<li><strong>AWS</strong>: SCPs (Service Control Policies) em Organizations. "
                    "AWS Config Rules + Conformance Packs. Trusted Advisor. Security Hub.</li>"
                    "<li><strong>Azure</strong>: Azure Policy (deny/audit/append). "
                    "Defender for Cloud.</li>"
                    "<li><strong>GCP</strong>: Organization Policies. Security Command Center.</li>"
                    "<li><strong>Multi-cloud</strong>: <strong>Cloud Custodian</strong> "
                    "(open source), Wiz, Prisma Cloud, Lacework.</li>"
                    "</ul>"
                    "<p>Exemplo de SCP que impede S3 público:</p>"
                    "<pre><code>{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [{\n"
                    "    \"Effect\": \"Deny\",\n"
                    "    \"Action\": [\"s3:PutBucketPublicAccessBlock\"],\n"
                    "    \"Resource\": \"*\",\n"
                    "    \"Condition\": {\n"
                    "      \"StringNotEquals\": {\"s3:PublicAccessBlock\": \"true\"}\n"
                    "    }\n"
                    "  }]\n"
                    "}</code></pre>"

                    "<h3>7. Como ler a documentação do provedor</h3>"
                    "<p>Cada serviço tem matriz de responsabilidade. Em ambientes regulados:</p>"
                    "<ul>"
                    "<li>Service Specific Terms (AWS) / Service Description (Azure).</li>"
                    "<li>Data Processing Addendum (DPA), exigência LGPD/GDPR.</li>"
                    "<li>Trust &amp; Compliance Center: ISO 27001, SOC 2, PCI, HIPAA.</li>"
                    "<li>Customer Compliance Guides: o que é seu e o que é deles.</li>"
                    "</ul>"
                    "<p>Não assine contrato sem ler isso. Em incidente, a primeira pergunta "
                    "do auditor é 'mostre o contrato e o controle correspondente'.</p>"

                    "<h3>8. Modelo PaaS = mais cuidado, não menos</h3>"
                    "<p>'Lambda é serverless, não tem servidor para patchear, então não "
                    "preciso de nada', <strong>mito</strong>. Em FaaS você ainda é "
                    "responsável por:</p>"
                    "<ul>"
                    "<li>Vulnerabilidades nas suas dependências (Log4Shell em Lambda Java).</li>"
                    "<li>Permissões IAM (role da Lambda com S3:* é receita de SSRF).</li>"
                    "<li>Validação de input.</li>"
                    "<li>Segredos e gestão de chaves.</li>"
                    "<li>Logs e monitoring (sim, Lambda também precisa).</li>"
                    "</ul>"
                    "<p>O provedor cuida de menos camadas, mas o que sobra é exatamente "
                    "onde estão as 10 vulnerabilidades mais comuns (OWASP Top 10).</p>"

                    "<h3>9. Caso real: Capital One 2019, anatomia de uma violação cloud</h3>"
                    "<ol>"
                    "<li>WAF mal configurado (problema do <em>cliente</em>) permitia SSRF.</li>"
                    "<li>SSRF para <code>http://169.254.169.254/latest/meta-data/iam/...</code> "
                    "(metadata service da AWS) retornou credenciais temporárias da role da "
                    "EC2.</li>"
                    "<li>Role tinha <code>s3:ListAllMyBuckets</code> e "
                    "<code>s3:GetObject</code> em <em>todos os buckets da empresa</em>, "
                    "violação de PoLP (problema do <em>cliente</em>).</li>"
                    "<li>Atacante listou e baixou, 100M de registros vazados.</li>"
                    "</ol>"
                    "<p>Em <strong>nenhum</strong> momento a AWS falhou. A 'cloud' funcionou "
                    "perfeitamente. Os controles do <em>cliente</em> que falharam: WAF, IAM, "
                    "rede, monitoring (não detectou exfiltração).</p>"
                    "<p>Resposta da AWS depois disso: lançou IMDSv2 (token-based, requer "
                    "<code>PUT</code>) que mitiga SSRF; ativou Block Public Access default "
                    "em buckets novos; lançou IAM Access Analyzer. Mas nenhuma dessas "
                    "mudanças <em>tira</em> sua responsabilidade, só facilita acertar.</p>"

                    "<h3>10. Checklist mensal de Shared Responsibility</h3>"
                    "<ol>"
                    "<li>Conta root tem MFA hardware? (Não use root no dia-a-dia.)</li>"
                    "<li>CloudTrail ativo em <em>todas</em> as regiões? Logs em bucket "
                    "imutável separado?</li>"
                    "<li>Block Public Access ativado em conta inteira?</li>"
                    "<li>SCP/Policy bloqueando criação de recursos sem encryption?</li>"
                    "<li>SCP/Policy bloqueando regiões fora das aprovadas?</li>"
                    "<li>Security Hub / Defender / SCC habilitado e revisado?</li>"
                    "<li>GuardDuty / Defender for Cloud / SCC com alerta crítico encaminhado?</li>"
                    "<li>Backups configurados e <em>testados</em> em todos os RDS?</li>"
                    "<li>Access keys do IAM com idade &gt; 90 dias rotacionadas?</li>"
                    "<li>Resources tagueados com <code>Owner</code> e <code>Environment</code>?</li>"
                    "</ol>"
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
                  ["Patch do app do cliente.",
                   "Configurar IAM do cliente.",
                   "Backup do banco do cliente."],
                  "DA cloud (segurança da infraestrutura) é do provedor; NA cloud (o que você roda nela) é seu."),
                q("Em SaaS típico, o que ainda é dever do cliente?",
                  "Identidades, dados e configuração.",
                  ["Hardware.",
                   "Sistema operacional.",
                   "Hypervisor."],
                  "Mesmo no SaaS, gerência de usuários, MFA e classificação de dados não saem do cliente."),
                q("Quem responde por uma S3 mal configurado e público?",
                  "O cliente, é configuração dele.",
                  ["Sempre o provedor.",
                   "É bug da AWS.",
                   "Compartilhado."],
                  "AWS oferece 'Block Public Access' habilitado por padrão; cliente desligou? Cliente respondeu."),
                q("Backup de dados em RDS é dever:",
                  "Do cliente, a AWS oferece a infraestrutura, mas o cliente configura snapshots e retenção.",
                  ["Do provedor sempre.",
                   "Não existe backup em RDS.",
                   "Da auditoria externa."],
                  "Snapshots automáticos têm retenção padrão curta; ajuste para sua janela de RTO/RPO."),
                q("Qual fator NÃO faz parte do shared responsibility?",
                  "Cor do logo da empresa.",
                  ["Identidade.",
                   "Dados.",
                   "Rede virtual."],
                  "Pegadinha, todos os outros são partes legítimas do modelo."),
                q("Em IaaS, patch do kernel é:",
                  "Responsabilidade do cliente.",
                  ["Responsabilidade do provedor.",
                   "Não precisa ser feito.",
                   "Automatizado pela cloud."],
                  "Use Systems Manager/Update Management para automatizar, mas a responsabilidade é sua."),
                q("Compliance é responsabilidade:",
                  "Compartilhada, cada parte certifica o que controla.",
                  ["Apenas do provedor.",
                   "Apenas do cliente.",
                   "Apenas do auditor."],
                  "Provedor mostra que o datacenter está conforme; cliente mostra que sua app/processo está conforme."),
                q("Por que ler documentos do provedor?",
                  "Para saber o limite exato e não pressupor cobertura.",
                  ["Por exigência legal apenas.",
                   "Para virar parceiro.",
                   "Para reduzir custos."],
                  "Surpresas em incidente são caras; ler antes evita 'nossa, achei que vocês cuidassem disso'."),
                q("Configuração errada em segurança em cloud é a causa:",
                  "Mais comum de incidentes em cloud pública.",
                  ["Mais rara.",
                   "Apenas de problemas de billing.",
                   "Sempre culpa do provedor."],
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
                    "<h3>1. Identidades: humanas vs máquina</h3>"
                    "<p>Existem dois grandes grupos:</p>"
                    "<ul>"
                    "<li><strong>Humanas</strong>: devs, ops, financeiro, vendas. Acessam "
                    "console e CLI. Devem ser federadas via SSO (IAM Identity Center, Entra "
                    "ID, Google Workspace) com MFA forte (idealmente FIDO2/hardware key).</li>"
                    "<li><strong>De máquina (workload)</strong>: aplicações, pipelines, "
                    "agentes. Devem usar credenciais <em>temporárias</em>: roles assumidas "
                    "via STS, IRSA (EKS), Workload Identity (GKE), Managed Identity (Azure), "
                    "OIDC para CI/CD.</li>"
                    "</ul>"
                    "<p>Anti-pattern grave: humano usar credencial de máquina (chave estática "
                    "de uma role) ou app usar credencial humana (chave do dev rodando em "
                    "produção). Cada um tem seu fluxo.</p>"

                    "<h3>2. Estrutura de uma policy IAM (AWS)</h3>"
                    "<p>Policy é um documento JSON. Anatomia:</p>"
                    "<pre><code>{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [\n"
                    "    {\n"
                    "      \"Sid\": \"ReadReports\",\n"
                    "      \"Effect\": \"Allow\",\n"
                    "      \"Action\": [\n"
                    "        \"s3:GetObject\",\n"
                    "        \"s3:ListBucket\"\n"
                    "      ],\n"
                    "      \"Resource\": [\n"
                    "        \"arn:aws:s3:::reports-prod\",\n"
                    "        \"arn:aws:s3:::reports-prod/*\"\n"
                    "      ],\n"
                    "      \"Condition\": {\n"
                    "        \"StringEquals\": {\n"
                    "          \"aws:SourceVpc\": \"vpc-0abc123\"\n"
                    "        },\n"
                    "        \"Bool\": {\n"
                    "          \"aws:MultiFactorAuthPresent\": \"true\"\n"
                    "        },\n"
                    "        \"DateGreaterThan\": {\n"
                    "          \"aws:CurrentTime\": \"2026-01-01T00:00:00Z\"\n"
                    "        }\n"
                    "      }\n"
                    "    }\n"
                    "  ]\n"
                    "}</code></pre>"
                    "<p>Cada Statement tem:</p>"
                    "<ul>"
                    "<li><code>Effect</code>: Allow ou Deny.</li>"
                    "<li><code>Action</code>: lista de operações (<code>s3:GetObject</code>, "
                    "<code>ec2:RunInstances</code>...). Use wildcards com cuidado.</li>"
                    "<li><code>Resource</code>: ARNs específicos.</li>"
                    "<li><code>Condition</code>: contexto opcional.</li>"
                    "</ul>"

                    "<h3>3. Avaliação: como o IAM decide</h3>"
                    "<p>Algoritmo de avaliação (simplificado):</p>"
                    "<ol>"
                    "<li>Por padrão, tudo é negado.</li>"
                    "<li>SCPs (Organizations) restringem o universo do possível. Se SCP "
                    "negar, acabou, nem o admin da conta pode.</li>"
                    "<li>Resource policy (ex.: bucket policy) ou identity policy explícita "
                    "como <em>Allow</em> permite.</li>"
                    "<li><strong>Qualquer Deny explícito</strong> sobrescreve qualquer Allow.</li>"
                    "<li>Permission boundaries (em IAM users/roles) são teto adicional.</li>"
                    "</ol>"
                    "<p>Resumido: <code>SCP ∩ (Policy ∪ ResourcePolicy) ∩ Boundary − Deny</code>.</p>"

                    "<h3>4. Roles &gt; usuários, sempre</h3>"
                    "<p>Diferenças críticas:</p>"
                    "<table>"
                    "<tr><th></th><th>User</th><th>Role</th></tr>"
                    "<tr><td>Credencial</td><td>permanente (chave/senha)</td>"
                    "<td>temporária (~15min-12h via STS)</td></tr>"
                    "<tr><td>Quem usa</td><td>geralmente humano</td><td>qualquer principal "
                    "que assuma (humano, app, outra conta, OIDC)</td></tr>"
                    "<tr><td>Vazamento</td><td>vale para sempre até rotacionar</td>"
                    "<td>expira sozinha</td></tr>"
                    "<tr><td>Auditoria</td><td>'user X fez Y'</td>"
                    "<td>'user X assumiu role R e fez Y'</td></tr>"
                    "</table>"
                    "<p>Recomendação moderna: <strong>zero usuários IAM</strong> em produção. "
                    "Tudo via federação SSO (humanos) e roles assumidas (apps).</p>"

                    "<h3>5. CI/CD com OIDC, fim das chaves estáticas</h3>"
                    "<p>Anti-pattern clássico: armazenar AWS access key como secret no GitHub "
                    "Actions / GitLab CI. Vaza, vira RCE permanente em produção.</p>"
                    "<p>Padrão moderno: <strong>OIDC federation</strong>. O CI provider "
                    "emite um JWT com claims (repo, branch, workflow); AWS verifica e troca "
                    "por credenciais temporárias.</p>"
                    "<pre><code># Trust policy da role (quem pode assumir)\n"
                    "{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [{\n"
                    "    \"Effect\": \"Allow\",\n"
                    "    \"Principal\": {\n"
                    "      \"Federated\": \"arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com\"\n"
                    "    },\n"
                    "    \"Action\": \"sts:AssumeRoleWithWebIdentity\",\n"
                    "    \"Condition\": {\n"
                    "      \"StringEquals\": {\n"
                    "        \"token.actions.githubusercontent.com:aud\": \"sts.amazonaws.com\"\n"
                    "      },\n"
                    "      \"StringLike\": {\n"
                    "        \"token.actions.githubusercontent.com:sub\": \"repo:myorg/myrepo:ref:refs/heads/main\"\n"
                    "      }\n"
                    "    }\n"
                    "  }]\n"
                    "}</code></pre>"
                    "<pre><code># GitHub Actions workflow\n"
                    "permissions:\n"
                    "  id-token: write\n"
                    "  contents: read\n"
                    "\n"
                    "jobs:\n"
                    "  deploy:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with:\n"
                    "          role-to-assume: arn:aws:iam::123:role/github-deploy\n"
                    "          aws-region: us-east-1\n"
                    "      - run: aws s3 sync ./dist s3://bucket/</code></pre>"
                    "<p>Sem chave estática, sem rotação, sem vazamento crítico. O JWT vive "
                    "minutos.</p>"

                    "<h3>6. Hierarquia organizacional, guard-rails</h3>"
                    "<p>Em organizações sérias, contas (AWS) ou subscriptions (Azure) ou "
                    "projects (GCP) são organizadas em árvore:</p>"
                    "<pre><code>Root\n"
                    "├── OU Production\n"
                    "│   ├── account: prod-app-frontend\n"
                    "│   └── account: prod-app-backend\n"
                    "├── OU NonProd\n"
                    "│   ├── account: staging\n"
                    "│   └── account: dev\n"
                    "├── OU Sandbox\n"
                    "│   └── account: dev-experiments  (alta liberdade, isolada)\n"
                    "└── OU Security\n"
                    "    ├── account: log-archive  (CloudTrail centralizado)\n"
                    "    └── account: audit         (read-only para compliance)</code></pre>"
                    "<p>SCPs aplicadas em OU descem para todas as contas filhas. Exemplos "
                    "úteis:</p>"
                    "<ul>"
                    "<li>'Negue todas as ações fora das regiões aprovadas.'</li>"
                    "<li>'Negue criação de IAM user em conta de produção.'</li>"
                    "<li>'Negue desligar CloudTrail.'</li>"
                    "<li>'Negue criação de bucket sem encryption.'</li>"
                    "</ul>"

                    "<h3>7. Conditions: o segredo das policies poderosas</h3>"
                    "<p>Condition keys mais úteis (AWS):</p>"
                    "<ul>"
                    "<li><code>aws:MultiFactorAuthPresent</code> / <code>aws:MultiFactorAuthAge</code></li>"
                    "<li><code>aws:SourceIp</code> / <code>aws:VpcSourceIp</code></li>"
                    "<li><code>aws:SourceVpc</code> / <code>aws:SourceVpce</code></li>"
                    "<li><code>aws:RequestedRegion</code></li>"
                    "<li><code>aws:CurrentTime</code> (limitar horário)</li>"
                    "<li><code>aws:ResourceTag/&lt;tag&gt;</code> (ABAC)</li>"
                    "<li><code>aws:PrincipalTag/&lt;tag&gt;</code></li>"
                    "<li><code>aws:SecureTransport</code> (forçar HTTPS)</li>"
                    "</ul>"
                    "<p>ABAC (Attribute-Based Access Control): em vez de role por equipe, "
                    "use tags em recursos e principais. Policy: 'usuário com "
                    "<code>team=alpha</code> pode acessar recurso com "
                    "<code>team=alpha</code>'. Escala muito melhor.</p>"

                    "<h3>8. Auditoria: CloudTrail, GuardDuty, Access Analyzer</h3>"
                    "<ul>"
                    "<li><strong>CloudTrail</strong>: registra cada chamada de API. Habilite "
                    "trail org-wide encaminhando para bucket em conta separada (log-archive) "
                    "com object-lock. Sem isso, atacante apaga logs.</li>"
                    "<li><strong>GuardDuty</strong>: detecção comportamental "
                    "(API anômala, mineração de crypto, exfiltração).</li>"
                    "<li><strong>IAM Access Analyzer</strong>: gera relatório do que cada "
                    "principal <em>realmente usou</em> nos últimos 90 dias. Use para "
                    "podar permissões não usadas.</li>"
                    "<li><strong>Access Advisor</strong>: 'serviço Y nunca foi acessado por "
                    "esta role'. Remova.</li>"
                    "</ul>"

                    "<h3>9. Azure Entra ID e GCP IAM, equivalentes</h3>"
                    "<p>Em Azure:</p>"
                    "<ul>"
                    "<li><strong>Entra ID</strong> (antigo Azure AD): identidade.</li>"
                    "<li><strong>RBAC</strong>: built-in roles (Reader, Contributor, Owner) "
                    "ou custom. Aplica em scope (subscription/resource group/resource).</li>"
                    "<li><strong>Conditional Access</strong>: 'só permite login se MFA + "
                    "device compliant + IP corporativo'. Granular e poderoso.</li>"
                    "<li><strong>PIM</strong> (Privileged Identity Management): just-in-time "
                    "access, você 'eleva' temporariamente para Owner com aprovação.</li>"
                    "</ul>"
                    "<p>Em GCP:</p>"
                    "<ul>"
                    "<li>IAM com bindings (member → role → resource). Predefined roles + "
                    "custom roles.</li>"
                    "<li>Resource Hierarchy: Organization → Folders → Projects → "
                    "Resources.</li>"
                    "<li>Workload Identity: substitui chave de service account.</li>"
                    "<li>Org Policies: guard-rails.</li>"
                    "</ul>"

                    "<h3>10. Anti-patterns clássicos</h3>"
                    "<ul>"
                    "<li>Conta root com chaves estáticas em uso diário. <strong>NUNCA.</strong></li>"
                    "<li>Access key em <code>git push</code> público, vaza em &lt;1h "
                    "(scanners de bots).</li>"
                    "<li>Role <code>AdministratorAccess</code> em app de produção 'porque "
                    "estava dando erro'.</li>"
                    "<li>Sem MFA em ninguém ou MFA SMS (vulnerável a SIM swap).</li>"
                    "<li>Permission creep, todo mundo só adiciona, ninguém remove.</li>"
                    "<li>Sem CloudTrail ou CloudTrail em região única.</li>"
                    "<li>Mesma role usada por 50 apps diferentes (porque 'é mais simples').</li>"
                    "<li>Sem rotação de access keys.</li>"
                    "<li>Senha sem complexidade ou sem rotação periódica.</li>"
                    "<li>Compartilhamento de credenciais entre humanos ('login do time').</li>"
                    "</ul>"

                    "<h3>11. Caso real: Uber 2022</h3>"
                    "<p>Atacante comprou credenciais de funcionário Uber na dark web. "
                    "Bombardeou push notifications de MFA até o funcionário aprovar 'só para "
                    "parar' (MFA fatigue). Dentro da rede, encontrou um script PowerShell em "
                    "share interno com credenciais hard-coded de uma conta Privileged Access "
                    "Management. Com isso, escalou para Vault, AWS, GCP, GSuite. Lições:</p>"
                    "<ul>"
                    "<li>MFA SMS / push é vulnerável a fadiga. Use FIDO2/hardware token.</li>"
                    "<li>Number matching (Microsoft) ou hardware key resolveriam.</li>"
                    "<li>Credenciais hard-coded em scripts internos = bomba relógio.</li>"
                    "<li>PAM precisa estar separado, com MFA reforçado.</li>"
                    "</ul>"
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
                  ["Mais rápido.",
                   "Maior cota.",
                   "Mais barato."],
                  "Chave temporária expira sozinha; chave estática vaza e fica em open-source forever."),
                q("MFA serve para:",
                  "Adicionar segundo fator (algo que você tem) à autenticação.",
                  ["Substituir senha.",
                   "Aumentar quota.",
                   "Gerar tokens DNS."],
                  "Reduz drasticamente o risco de credential stuffing, mesmo se a senha vaza, MFA segura."),
                q("Policy IAM é avaliada como:",
                  "Combinação de Allow/Deny, Deny sempre vence em conflito.",
                  ["Last write wins.",
                   "Apenas o último Allow.",
                   "Random."],
                  "Sem Allow explícito, default é negar. Deny sempre wins, mesmo se houver Allow em outra policy."),
                q("Para devs sem precisar de console, prefira:",
                  "Roles e federação (IAM Identity Center / SSO).",
                  ["Usuário IAM com chave.",
                   "Compartilhar credenciais.",
                   "Senha por SMS."],
                  "Acesso temporário emitido por SSO; nada de chave longa flutuando em ~/.aws/credentials."),
                q("SCP em AWS Organizations serve para:",
                  "Criar guardrails que limitam o que contas filhas podem fazer.",
                  ["Aumentar billing.",
                   "Substituir VPC.",
                   "Acelerar deploys."],
                  "SCP é teto: mesmo Admin de uma sub-conta não escapa. Útil para impor compliance."),
                q("Por que rotacionar access keys?",
                  "Limita o impacto se uma chave vazar.",
                  ["Aumenta velocidade.",
                   "Reduz custo.",
                   "Necessário para HTTPS."],
                  "Janela de exploração de uma chave vazada é o tempo entre vazamento e próxima rotação."),
                q("Como aplicar PoLP em IAM?",
                  "Conceder apenas as ações e recursos estritamente necessários.",
                  ["Dar AdministratorAccess.",
                   "Permitir tudo no início.",
                   "Ignorar policies."],
                  "Comece restrito; relaxe só se a app realmente precisar. Use Access Analyzer para encontrar excessos."),
                q("Qual recurso registra quem fez o quê na AWS?",
                  "AWS CloudTrail.",
                  ["S3 logs apenas.",
                   "VPC Flow Logs.",
                   "Athena."],
                  "CloudTrail registra calls de API. Habilitar org-wide trail e enviar para bucket protegido."),
                q("Diferença entre user e role:",
                  "User tem credenciais permanentes; role é assumida temporariamente.",
                  ["Role custa mais.",
                   "User é só para humanos.",
                   "Role não pode ser usada por humanos."],
                  "Humano pode assumir role via SSO; máquina via STS AssumeRole. Ambos podem."),
                q("Recomendação para conta root:",
                  "Não usar para tarefas diárias e ativar MFA forte.",
                  ["Usar para tudo.",
                   "Compartilhar com o time.",
                   "Desativar MFA."],
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
                    "<h3>1. Anatomia de uma VPC</h3>"
                    "<p>Uma VPC é uma rede privada virtual:</p>"
                    "<ul>"
                    "<li>CIDR principal (ex.: <code>10.0.0.0/16</code> = 65k IPs).</li>"
                    "<li>Pode ter CIDRs secundários (até 5).</li>"
                    "<li>Existe em uma região (cobre todas as AZs dessa região).</li>"
                    "<li>É isolada por padrão, sem internet, sem outras VPCs.</li>"
                    "</ul>"
                    "<p>Dentro da VPC:</p>"
                    "<ul>"
                    "<li><strong>Subnets</strong>: blocos CIDR menores, cada um em uma AZ.</li>"
                    "<li><strong>Route Tables</strong>: para onde vai cada pacote.</li>"
                    "<li><strong>Internet Gateway (IGW)</strong>: dá conectividade pública.</li>"
                    "<li><strong>NAT Gateway</strong>: saída privada para internet.</li>"
                    "<li><strong>Security Groups, NACLs</strong>: filtros (próxima aula).</li>"
                    "<li><strong>VPC Endpoints</strong>: acesso privado a serviços do "
                    "provedor.</li>"
                    "</ul>"

                    "<h3>2. Planejamento de IP, pense agora, sofra menos depois</h3>"
                    "<p>Mudar CIDR de VPC ativa é difícil. Planeje com folga:</p>"
                    "<ul>"
                    "<li><strong>VPC inteira</strong>: <code>/16</code> (65k IPs) é o "
                    "padrão razoável.</li>"
                    "<li><strong>Subnets</strong>: <code>/24</code> (256 IPs) para apps "
                    "pequenas, <code>/22</code> (1024 IPs) para apps grandes (K8s precisa de "
                    "muito IP).</li>"
                    "<li><strong>Reserve faixas</strong>: ambiente prod, staging, dev em "
                    "ranges diferentes; permite peering futuro sem conflito.</li>"
                    "<li><strong>Não use ranges populares</strong>: "
                    "<code>10.0.0.0/16</code>, <code>172.31.0.0/16</code> (default AWS), "
                    "<code>192.168.1.0/24</code> são candidatos óbvios para conflito com "
                    "VPN, on-prem ou outras VPCs.</li>"
                    "</ul>"
                    "<p>Plano típico para uma org média:</p>"
                    "<pre><code>10.0.0.0/8       - todo o universo corporativo\n"
                    "  10.0.0.0/12  - prod   (10.0.0.0  - 10.15.255.255)\n"
                    "  10.16.0.0/12 - staging\n"
                    "  10.32.0.0/12 - dev\n"
                    "  10.48.0.0/12 - sandbox\n"
                    "Cada VPC: /16 dentro do bloco apropriado\n"
                    "Cada subnet: /22 ou /24 dentro da VPC</code></pre>"

                    "<h3>3. Subnets pública e privada</h3>"
                    "<p>A diferença é apenas <em>roteamento</em>:</p>"
                    "<ul>"
                    "<li><strong>Pública</strong>: route table tem rota "
                    "<code>0.0.0.0/0 → IGW</code>. Recursos com IP público recebem "
                    "internet.</li>"
                    "<li><strong>Privada</strong>: route table tem rota "
                    "<code>0.0.0.0/0 → NAT Gateway</code>. Saída para internet, sem "
                    "entrada direta.</li>"
                    "<li><strong>Isolada</strong>: sem rota para internet. Saída só via "
                    "VPC Endpoints (S3, DynamoDB, etc.).</li>"
                    "</ul>"
                    "<p>Padrão tradicional 'three-tier':</p>"
                    "<pre><code>VPC 10.0.0.0/16\n"
                    "├── Public  10.0.1.0/24  (AZ a)  - ALB\n"
                    "├── Public  10.0.2.0/24  (AZ b)  - ALB\n"
                    "├── Private 10.0.10.0/24 (AZ a)  - app servers\n"
                    "├── Private 10.0.11.0/24 (AZ b)  - app servers\n"
                    "├── Isolated 10.0.20.0/24 (AZ a) - RDS\n"
                    "└── Isolated 10.0.21.0/24 (AZ b) - RDS</code></pre>"
                    "<p>ALB recebe internet, fala com app em privada, app fala com banco em "
                    "isolada. Banco nunca toca internet.</p>"

                    "<h3>4. NAT Gateway, útil mas caro</h3>"
                    "<p>Permite saída de subnets privadas. Custo na AWS:</p>"
                    "<ul>"
                    "<li>~US$ 32/mês por NAT Gateway (apenas existir).</li>"
                    "<li>+US$ 0.045/GB processado.</li>"
                    "<li>Multiplique por AZ (HA exige um por AZ).</li>"
                    "</ul>"
                    "<p>Em apps que baixam muitos GB de pacotes, isso domina a fatura. "
                    "Mitigações:</p>"
                    "<ul>"
                    "<li><strong>VPC Endpoints (S3, DynamoDB)</strong>: tráfego para esses "
                    "serviços nem chega no NAT.</li>"
                    "<li><strong>Mirror interno</strong> de pacotes (Artifactory, ECR).</li>"
                    "<li><strong>NAT instances customizadas</strong> para volumes grandes "
                    "(mais barato em alguns casos).</li>"
                    "<li><strong>Single NAT Gateway</strong> em ambientes não-prod (perde "
                    "HA mas economiza).</li>"
                    "</ul>"

                    "<h3>5. Conectividade VPC ↔ VPC ↔ on-prem</h3>"
                    "<table>"
                    "<tr><th>Opção</th><th>Caso de uso</th><th>Limite</th></tr>"
                    "<tr><td>VPC Peering</td><td>Conectar 2 VPCs com IPs distintos</td>"
                    "<td>1:1, sem trânsito (não 'roteia' entre peerings)</td></tr>"
                    "<tr><td>Transit Gateway</td><td>Hub-and-spoke para muitas VPCs e "
                    "on-prem</td><td>Custo por hora + por GB</td></tr>"
                    "<tr><td>VPN Site-to-Site</td><td>Conectar on-prem via internet "
                    "(IPsec)</td><td>Latência variável, ~1 Gbps</td></tr>"
                    "<tr><td>Direct Connect</td><td>Linha dedicada para on-prem</td>"
                    "<td>Caro, latência baixa, alta banda (até 100 Gbps)</td></tr>"
                    "<tr><td>VPC Endpoint (Gateway)</td><td>Acesso privado a S3/DynamoDB</td>"
                    "<td>Só esses dois serviços; gratuito</td></tr>"
                    "<tr><td>VPC Endpoint (Interface)</td>"
                    "<td>Acesso privado a outros serviços via PrivateLink</td>"
                    "<td>~US$ 7/mês por endpoint por AZ</td></tr>"
                    "<tr><td>PrivateLink</td><td>Expor seu serviço para outras contas "
                    "privadamente</td><td>Sem trânsito; 1:1</td></tr>"
                    "</table>"

                    "<h3>6. VPC Endpoints, economia e segurança</h3>"
                    "<p>Sem endpoint: sua EC2 em subnet privada chama S3, tráfego sai pela "
                    "internet via NAT, ida e volta. Com endpoint: tráfego nunca sai da rede "
                    "AWS, é mais barato (sem custo de NAT) e mais seguro (não passa por "
                    "internet).</p>"
                    "<pre><code>resource \"aws_vpc_endpoint\" \"s3\" {\n"
                    "  vpc_id            = aws_vpc.main.id\n"
                    "  service_name      = \"com.amazonaws.us-east-1.s3\"\n"
                    "  vpc_endpoint_type = \"Gateway\"\n"
                    "  route_table_ids   = [aws_route_table.private.id]\n"
                    "  policy = jsonencode({\n"
                    "    Statement = [{\n"
                    "      Effect = \"Allow\",\n"
                    "      Principal = \"*\",\n"
                    "      Action = [\"s3:GetObject\", \"s3:PutObject\"],\n"
                    "      Resource = [\n"
                    "        \"arn:aws:s3:::meus-buckets/*\"\n"
                    "      ]\n"
                    "    }]\n"
                    "  })\n"
                    "}</code></pre>"
                    "<p>A policy do endpoint pode <em>limitar</em> qual bucket é acessado, "
                    "mesmo que IAM permita, se endpoint nega, está negado.</p>"

                    "<h3>7. VPC Flow Logs, auditoria</h3>"
                    "<p>Registra metadados (não payload) de cada pacote em uma ENI:</p>"
                    "<pre><code>resource \"aws_flow_log\" \"main\" {\n"
                    "  log_destination = aws_s3_bucket.flow_logs.arn\n"
                    "  log_destination_type = \"s3\"\n"
                    "  traffic_type    = \"ALL\"\n"
                    "  vpc_id          = aws_vpc.main.id\n"
                    "}</code></pre>"
                    "<p>Útil para:</p>"
                    "<ul>"
                    "<li>Investigar 'por que esse SG está bloqueando?' (REJECT logs).</li>"
                    "<li>Detectar exfiltração (volume anômalo saindo).</li>"
                    "<li>Compliance (PCI exige logs de tráfego).</li>"
                    "<li>Análise de custo (descobrir quem fala com quem).</li>"
                    "</ul>"

                    "<h3>8. Limitações e armadilhas</h3>"
                    "<ul>"
                    "<li>CIDRs <strong>não podem se sobrepor</strong> entre VPCs que vão "
                    "se conectar (peering, TGW). Pegou esse problema 6 meses depois? "
                    "Migração dolorosa.</li>"
                    "<li>AWS reserva 5 IPs em cada subnet (.0 rede, .1 router, .2 DNS, .3 "
                    "futuro, último broadcast). <code>/28</code> dá 11 utilizáveis.</li>"
                    "<li>Subnet existe em apenas <em>uma</em> AZ. HA = mínimo 2 subnets "
                    "(em AZs diferentes) por camada.</li>"
                    "<li>Default VPC vem com config insegura, apague em contas de "
                    "produção (ou pelo menos não use).</li>"
                    "<li><strong>VPC peering não é transitivo</strong>: A peering B, B "
                    "peering C, A <em>não</em> fala com C. Use TGW para isso.</li>"
                    "</ul>"

                    "<h3>9. Segurança em camadas</h3>"
                    "<p>Defesa em profundidade no nível de rede:</p>"
                    "<ol>"
                    "<li><strong>VPC isolada</strong>: dado sensível em VPC dedicada (ex.: "
                    "PCI scope).</li>"
                    "<li><strong>Subnet isolada</strong>: banco sem rota para internet.</li>"
                    "<li><strong>NACL</strong>: bloqueio amplo por subnet.</li>"
                    "<li><strong>Security Group</strong>: regra fina por instância.</li>"
                    "<li><strong>Host firewall</strong>: ufw/nftables como rede de segurança.</li>"
                    "<li><strong>Aplicação</strong>: WAF, autenticação, autorização.</li>"
                    "</ol>"
                    "<p>Cada camada deve assumir que a anterior pode falhar.</p>"

                    "<h3>10. Caso real: o NAT Gateway de US$ 80k</h3>"
                    "<p>Em 2022, uma startup compartilhou que tinha conta de US$ 80k em um "
                    "mês só de NAT Gateway porque o ML pipeline baixava modelos de Hugging "
                    "Face do S3 público (saía pelo NAT, entrava pelo NAT, voltava por "
                    "internet). Solução: cache local + VPC Endpoint para S3 (porque a "
                    "imagem de Hugging Face é hospedada lá). Conta caiu para US$ 200/mês. "
                    "Lição: cada GB de egress por NAT Gateway é US$ 0.045. Em escala, isso "
                    "explode rápido.</p>"
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
                  ["Endereço IP.",
                   "Tabela de rotas.",
                   "Security Group."],
                  "Sem rota para IGW, instâncias não recebem tráfego direto da internet."),
                q("Para outbound de subnet privada:",
                  "Use NAT Gateway.",
                  ["Use Internet Gateway direto.",
                   "Não é possível.",
                   "Use Direct Connect apenas."],
                  "NAT Gateway permite saída sem expor a instância. Caro: considere VPC Endpoint quando o destino é AWS."),
                q("CIDR /16 em AWS VPC permite quantos hosts aproximadamente?",
                  "65 mil",
                  ["256", "1024", "infinitos"],
                  "/16 = 2^16 = 65.536 endereços. Subdivida em /24 (256 cada) ou /22, conforme necessidade."),
                q("VPC Peering serve para:",
                  "Conectar duas VPCs com IPs distintos.",
                  ["Conectar containers.",
                   "Substituir DNS.",
                   "Cobrar billing."],
                  "Peering é 1:1. Para muitas VPCs, use Transit Gateway (hub-and-spoke)."),
                q("Por que múltiplas AZs?",
                  "Resiliência a falhas de datacenter inteiro.",
                  ["Aumenta latência.",
                   "Reduz custo.",
                   "Não é recomendado."],
                  "AZ é unidade de falha; deploy multi-AZ é o mínimo para serviços de produção."),
                q("Route table define:",
                  "Para onde pacotes de uma subnet vão.",
                  ["Permissões IAM.",
                   "Tamanho do MTU.",
                   "Versão do TLS."],
                  "Cada destino (CIDR) tem next-hop (IGW, NAT, peering, gateway endpoint, etc.)."),
                q("Endpoint VPC para S3 reduz:",
                  "Tráfego que sai pela internet, vai pela rede da AWS.",
                  ["O custo do S3.",
                   "Latência para fora da AWS.",
                   "Necessidade de IAM."],
                  "Custos de NAT despencam e exposição também. Use Gateway Endpoint para S3/DynamoDB."),
                q("Internet Gateway é:",
                  "Recurso que permite conectividade bidirecional pública.",
                  ["Um proxy.",
                   "Um firewall.",
                   "Apenas IPv6."],
                  "IGW associado à VPC + rota 0.0.0.0/0 → IGW na route table = subnet pública."),
                q("Em VPC, qual recurso é stateful?",
                  "Security Groups.",
                  ["NACLs.",
                   "Subnets.",
                   "Route Tables."],
                  "SG entende a conexão (stateful). NACL é stateless, precisa configurar inbound E outbound."),
                q("CIDR sobreposto entre VPCs causa:",
                  "Problema em peering, não é permitido.",
                  ["Aceleração.",
                   "Backup automático.",
                   "Alta disponibilidade."],
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
                    "<h3>1. Security Group (SG): stateful, por interface</h3>"
                    "<p>SG é um conjunto de regras Allow associado a uma elastic network "
                    "interface (ENI). Características:</p>"
                    "<ul>"
                    "<li><strong>Stateful</strong>: se inbound 443/tcp é permitido, a "
                    "resposta sai automaticamente, não precisa regra outbound.</li>"
                    "<li><strong>Allow-only</strong>: não há regra Deny. Se nenhum SG "
                    "associado permite, é negado.</li>"
                    "<li><strong>Default</strong>: inbound nega tudo; outbound permite tudo. "
                    "Você pode (e deve, em ambientes sensíveis) restringir outbound.</li>"
                    "<li><strong>Por ENI</strong>: cada interface pode ter até 5 SGs (limite "
                    "ajustável).</li>"
                    "<li><strong>Mudança imediata</strong>: regra nova vale em segundos.</li>"
                    "</ul>"

                    "<h3>2. NACL: stateless, por subnet</h3>"
                    "<p>Network ACL é a 'camada de fora' que filtra na borda da subnet:</p>"
                    "<ul>"
                    "<li><strong>Stateless</strong>: precisa regras de inbound E outbound "
                    "para cada fluxo. Esquecer portas efêmeras (1024-65535 outbound) é "
                    "fonte clássica de 'meu serviço não responde'.</li>"
                    "<li><strong>Allow e Deny</strong>: avalia regras numericamente até "
                    "achar match.</li>"
                    "<li><strong>Default</strong>: NACL default permite tudo. NACLs custom "
                    "criadas começam negando tudo.</li>"
                    "<li><strong>Por subnet</strong>: aplica em todo tráfego que entra/sai "
                    "da subnet.</li>"
                    "</ul>"
                    "<p>Use NACL para:</p>"
                    "<ul>"
                    "<li>Bloqueio amplo (banir um IP de atacante de toda a subnet).</li>"
                    "<li>Compliance (regulação exige bloqueio de portas em determinada "
                    "subnet).</li>"
                    "<li>Camada extra de defesa (defesa em profundidade).</li>"
                    "</ul>"
                    "<p>Não use NACL para controle granular por instância, é o que SG faz "
                    "melhor.</p>"

                    "<h3>3. Encadeando SGs por referência (chain de SGs)</h3>"
                    "<p>Em vez de liberar porta por IP, libere por <strong>SG-id</strong>. "
                    "Padrão three-tier:</p>"
                    "<pre><code># SG do ALB\n"
                    "alb_sg:\n"
                    "  inbound:\n"
                    "    - 443/tcp from 0.0.0.0/0       # internet\n"
                    "    - 80/tcp from 0.0.0.0/0        # redireciona para 443\n"
                    "  outbound:\n"
                    "    - all to app_sg                # fala com app\n"
                    "\n"
                    "# SG dos app servers\n"
                    "app_sg:\n"
                    "  inbound:\n"
                    "    - 8000/tcp from alb_sg         # tráfego do ALB\n"
                    "  outbound:\n"
                    "    - 5432/tcp to db_sg            # postgres\n"
                    "    - 443/tcp to 0.0.0.0/0         # APIs externas\n"
                    "\n"
                    "# SG do banco\n"
                    "db_sg:\n"
                    "  inbound:\n"
                    "    - 5432/tcp from app_sg         # apenas app fala\n"
                    "  outbound: (nada)</code></pre>"
                    "<p>Vantagens:</p>"
                    "<ul>"
                    "<li>Regras seguem instâncias (auto-scaling adiciona instância? entra "
                    "no SG, ganha acesso).</li>"
                    "<li>Legível como diagrama de arquitetura.</li>"
                    "<li>Sem IP hard-coded.</li>"
                    "<li>Auditoria fácil.</li>"
                    "</ul>"

                    "<h3>4. Bastion vs SSM Session Manager</h3>"
                    "<p>Como acessar instâncias em subnet privada para SSH?</p>"
                    "<table>"
                    "<tr><th>Bastion clássico</th><th>SSM Session Manager (recomendado)</th></tr>"
                    "<tr><td>VM exposta com SSH em IP corporativo</td>"
                    "<td>Sem porta aberta; agente faz reverse tunnel</td></tr>"
                    "<tr><td>Chaves SSH espalhadas</td>"
                    "<td>Acesso via IAM (sem chave SSH em produção)</td></tr>"
                    "<tr><td>Auditoria via syslog do bastion</td>"
                    "<td>Auditoria automática em CloudTrail + S3 (cada comando)</td></tr>"
                    "<tr><td>Manutenção (patches, upgrades)</td>"
                    "<td>Sem instância para manter</td></tr>"
                    "<tr><td>Acesso via internet</td>"
                    "<td>Acesso via console ou CLI sem expor nada</td></tr>"
                    "</table>"
                    "<p>SSM uso:</p>"
                    "<pre><code>aws ssm start-session --target i-0abc123\n"
                    "# ou para port-forwarding (acessar RDS pelo seu laptop):\n"
                    "aws ssm start-session --target i-0abc123 \\\n"
                    "  --document-name AWS-StartPortForwardingSessionToRemoteHost \\\n"
                    "  --parameters host=mydb.cluster.us-east-1.rds.amazonaws.com,portNumber=5432,localPortNumber=5432</code></pre>"

                    "<h3>5. Outbound, restringir é boa prática</h3>"
                    "<p>Default do SG é outbound aberto. Em ambientes sensíveis, restrinja:</p>"
                    "<ul>"
                    "<li>App fala com banco (porta específica do banco, SG específico).</li>"
                    "<li>App fala com AWS APIs (use VPC Endpoints).</li>"
                    "<li>App fala com APIs externas conhecidas (porta 443 para domínios "
                    "específicos via egress proxy).</li>"
                    "</ul>"
                    "<p>Outbound restrito mata uma classe inteira de exfiltração e DNS "
                    "tunneling.</p>"

                    "<h3>6. Egress filtering com proxy</h3>"
                    "<p>Para ambientes com compliance pesado, force tráfego HTTPS para sair "
                    "via proxy explícito (Squid, mitmproxy) que aplica whitelist de domínios. "
                    "Combinado com SG outbound = só permitido falar com proxy, e proxy só "
                    "deixa passar para domínios autorizados.</p>"

                    "<h3>7. Anti-patterns recorrentes</h3>"
                    "<table>"
                    "<tr><td><code>0.0.0.0/0:22</code> em prod</td>"
                    "<td>Brute force constante. Sempre aparece em incidente.</td></tr>"
                    "<tr><td><code>0.0.0.0/0:3306</code> ou <code>:5432</code> em prod</td>"
                    "<td>Banco direto na internet. Ransomware aproveita.</td></tr>"
                    "<tr><td>SG 'allow-all' usado em tudo</td>"
                    "<td>Vira 'sem firewall' efetivo.</td></tr>"
                    "<tr><td>NACL custom com 'allow all' em primeira regra</td>"
                    "<td>Inútil; tira camada de defesa.</td></tr>"
                    "<tr><td>Liberar 0.0.0.0/0 'temporariamente' e esquecer</td>"
                    "<td>Use cron/expiry de tag para alertar regras temporárias.</td></tr>"
                    "<tr><td>Criar SG via console manual em vez de Terraform</td>"
                    "<td>Drift, sem auditoria, sem revisão.</td></tr>"
                    "</table>"

                    "<h3>8. Auditoria contínua</h3>"
                    "<ul>"
                    "<li><strong>VPC Flow Logs</strong>: vê tráfego permitido e rejeitado.</li>"
                    "<li><strong>AWS Config Rules</strong>: regra "
                    "'restricted-ssh' alerta SG com 22 aberto.</li>"
                    "<li><strong>Cloud Custodian</strong>: policy 'remediar SG com 0.0.0.0/0 "
                    "automaticamente após X horas'.</li>"
                    "<li><strong>Steampipe</strong>: SQL sobre tudo. "
                    "<code>select * from aws_vpc_security_group_rule where cidr_ipv4 = "
                    "'0.0.0.0/0' and from_port = 22</code>.</li>"
                    "<li><strong>Terraform plan</strong> em PR: revisão humana antes de "
                    "aplicar mudanças.</li>"
                    "</ul>"

                    "<h3>9. NACLs efêmeras e o pegadinha do NAT</h3>"
                    "<p>Tráfego de saída usando NAT Gateway sai pelo gateway com porta "
                    "efêmera. Resposta volta para essa porta. Se sua NACL outbound tem "
                    "'permit all' mas inbound tem só 443: <strong>resposta de uma "
                    "request HTTPS sua não passa</strong>. Solução: permita inbound "
                    "1024-65535 também (portas efêmeras).</p>"
                    "<pre><code># NACL inbound\n"
                    "100  allow 443/tcp  from 0.0.0.0/0   # se subnet pública\n"
                    "110  allow 1024-65535/tcp from 0.0.0.0/0  # respostas de outbound</code></pre>"

                    "<h3>10. Caso real: o RDP exposto</h3>"
                    "<p>Em 2023, o site Shadowserver reportou ~3.5 <em>milhões</em> de "
                    "servidores Windows com porta 3389 (RDP) expostos diretamente na "
                    "internet, incluindo gente em AWS/Azure. Bots automatizados fazem "
                    "brute-force constante. Em vez de expor RDP:</p>"
                    "<ul>"
                    "<li>Use Bastion Host com MFA + log + lockdown.</li>"
                    "<li>Melhor: AWS SSM ou Azure Bastion.</li>"
                    "<li>Restrict source IP para corporate VPN.</li>"
                    "<li>Network Level Authentication (NLA) sempre on.</li>"
                    "</ul>"
                    "<p>Custo de tirar RDP da internet: 1 dia de configuração. Custo de não "
                    "tirar: ransomware.</p>"
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
                  ["Stateless.",
                   "Apenas IPv6.",
                   "Aplicado por host físico."],
                  "Stateful = inbound libera o retorno do outbound automaticamente. NACL é o oposto."),
                q("NACL em AWS é:",
                  "Stateless, precisa regras de saída e entrada.",
                  ["Stateful.",
                   "Apenas IPv4.",
                   "Aplicado por instância."],
                  "Esquecer regra outbound de portas efêmeras é fonte clássica de 'meu serviço não responde'."),
                q("Por padrão, SG inbound:",
                  "Bloqueia tudo.",
                  ["Permite tudo.",
                   "Aceita 80 e 443.",
                   "Permite apenas SSH."],
                  "Default-deny, você precisa abrir explicitamente o que quer."),
                q("Em SG, posso permitir tráfego vindo de outro SG?",
                  "Sim, referenciando o SG-id no source.",
                  ["Não.",
                   "Apenas via IAM.",
                   "Apenas IPv6."],
                  "Encadeamento por SG é a melhor prática para evitar IP hardcoded."),
                q("NACL avalia regras:",
                  "Em ordem numérica até encontrar match.",
                  ["Aleatoriamente.",
                   "Por timestamp.",
                   "Apenas a última regra."],
                  "Por isso convenciona-se números (100, 200, 300...) e regra final 32766/deny all."),
                q("Para HTTPS, qual porta liberar?",
                  "443 TCP.",
                  ["80 UDP.",
                   "443 UDP.",
                   "8443 TCP somente."],
                  "443 TCP é o padrão; HTTP/3 usa 443 UDP, mas só libere se a app for HTTP/3."),
                q("SG aplica-se a:",
                  "Interfaces de rede (ENIs).",
                  ["Subnets inteiras.",
                   "Apenas IPv6.",
                   "Apenas Lambda."],
                  "ENI pode ter até 5 SGs (limite ajustável). Lambda em VPC também usa SG da ENI."),
                q("Boas práticas com SG:",
                  "Granularidade alta, sem 0.0.0.0/0 desnecessário.",
                  ["0.0.0.0/0 inbound em todas as portas.",
                   "Compartilhar um SG para tudo.",
                   "Não atualizar regras."],
                  "Granular = mais regras, mas auditável e principle of least access."),
                q("Permitir 0.0.0.0/0 em SSH é:",
                  "Risco crítico de força bruta.",
                  ["Boa prática.",
                   "Necessário para SSH.",
                   "Bloqueia o sshd."],
                  "Use bastion, VPN ou SSM Session Manager. SSH público em produção = manchete esperando acontecer."),
                q("Como auditar uso de SG?",
                  "VPC Flow Logs e CloudTrail.",
                  ["Apenas top do servidor.",
                   "DNS lookups.",
                   "Não é possível auditar."],
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
                    "<h3>1. Modelo de dados: object storage não é filesystem</h3>"
                    "<p>S3 não é POSIX:</p>"
                    "<ul>"
                    "<li>Não há diretórios reais, apenas <em>prefixos</em>. "
                    "<code>fotos/2025/janeiro/foo.jpg</code> é uma chave única.</li>"
                    "<li>Não há append nem rename, sobrescrever é re-upload completo.</li>"
                    "<li>Cada objeto = arquivo + metadados + tags + ACL.</li>"
                    "<li>Latência de listagem é alta para muitos prefixos; design data lake "
                    "com particionamento (Hive-style: "
                    "<code>year=2025/month=04/...</code>).</li>"
                    "<li>Consistência: read-after-write forte (mesmo após delete).</li>"
                    "</ul>"
                    "<p>Para casos onde você precisa de filesystem em S3, há "
                    "<strong>Mountpoint for S3</strong> ou <strong>s3fs-fuse</strong>, mas "
                    "saiba que <em>list</em> e <em>rename</em> são operações caras em S3.</p>"

                    "<h3>2. Controle de acesso, em ordem cronológica</h3>"
                    "<p>S3 acumulou camadas ao longo dos anos:</p>"
                    "<ol>"
                    "<li><strong>ACLs</strong> (legado): bucket/object owner + grants. "
                    "Hoje desabilitado por default. <strong>Não use.</strong></li>"
                    "<li><strong>Bucket Policies</strong> (resource-based): JSON anexado "
                    "ao bucket. Pode permitir cross-account, anonymous, etc.</li>"
                    "<li><strong>IAM Policies</strong> (identity-based): permissões da "
                    "identidade. Combinadas com bucket policy.</li>"
                    "<li><strong>Block Public Access</strong> (BPA): override 'segurança "
                    "primeiro'. Bloqueia tudo público mesmo que policies permitam.</li>"
                    "</ol>"
                    "<p>Regra de ouro: ative <strong>Block Public Access em conta inteira</strong>; "
                    "libere bucket público <em>apenas</em> quando o bucket for "
                    "explicitamente para CDN/site estático.</p>"

                    "<h3>3. Padrões de policy de bucket</h3>"
                    "<pre><code># Forçar HTTPS em todo o bucket\n"
                    "{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [{\n"
                    "    \"Sid\": \"DenyInsecureConnections\",\n"
                    "    \"Effect\": \"Deny\",\n"
                    "    \"Principal\": \"*\",\n"
                    "    \"Action\": \"s3:*\",\n"
                    "    \"Resource\": [\n"
                    "      \"arn:aws:s3:::meu-bucket\",\n"
                    "      \"arn:aws:s3:::meu-bucket/*\"\n"
                    "    ],\n"
                    "    \"Condition\": {\n"
                    "      \"Bool\": {\"aws:SecureTransport\": \"false\"}\n"
                    "    }\n"
                    "  }]\n"
                    "}\n"
                    "\n"
                    "# Cross-account leitura (delegação)\n"
                    "{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [{\n"
                    "    \"Effect\": \"Allow\",\n"
                    "    \"Principal\": {\"AWS\": \"arn:aws:iam::OUTRA_CONTA:role/data-reader\"},\n"
                    "    \"Action\": [\"s3:GetObject\", \"s3:ListBucket\"],\n"
                    "    \"Resource\": [\n"
                    "      \"arn:aws:s3:::meu-bucket\",\n"
                    "      \"arn:aws:s3:::meu-bucket/dataset/*\"\n"
                    "    ]\n"
                    "  }]\n"
                    "}</code></pre>"

                    "<h3>4. Upload seguro: presigned URL</h3>"
                    "<p>Anti-pattern: cliente faz upload via backend, que tunela bytes para "
                    "S3. Backend vira gargalo, paga banda dupla, e mantém credenciais.</p>"
                    "<p>Padrão correto: <strong>presigned URL</strong>. Backend gera URL "
                    "assinada com TTL curto (5min) e parâmetros restritos; cliente faz "
                    "upload <em>direto</em> para S3.</p>"
                    "<pre><code>import boto3\n"
                    "from botocore.config import Config\n"
                    "\n"
                    "s3 = boto3.client('s3', config=Config(signature_version='s3v4'))\n"
                    "\n"
                    "url = s3.generate_presigned_url(\n"
                    "    'put_object',\n"
                    "    Params={\n"
                    "        'Bucket': 'meu-bucket',\n"
                    "        'Key': f'uploads/{user_id}/{file_id}.jpg',\n"
                    "        'ContentType': 'image/jpeg',\n"
                    "        'ContentLength': 5_000_000,           # max 5 MB\n"
                    "        'Metadata': {'user-id': str(user_id)},\n"
                    "    },\n"
                    "    ExpiresIn=300,                            # 5 minutos\n"
                    ")\n"
                    "# Retorna ao cliente; ele faz PUT direto.</code></pre>"
                    "<p>Para mais segurança, use <strong>presigned POST</strong> que permite "
                    "policy-based constraints (size limits, content-type whitelist) que o "
                    "cliente não pode burlar.</p>"

                    "<h3>5. Encryption: SSE-S3, SSE-KMS, SSE-C, client-side</h3>"
                    "<table>"
                    "<tr><th>Modo</th><th>Chave gerenciada por</th><th>Auditoria</th><th>Caso de uso</th></tr>"
                    "<tr><td>SSE-S3</td><td>AWS</td><td>baixa</td>"
                    "<td>Default 'só ative algo'</td></tr>"
                    "<tr><td>SSE-KMS (AWS-managed)</td><td>AWS via KMS</td><td>média</td>"
                    "<td>Encryption padrão</td></tr>"
                    "<tr><td>SSE-KMS (CMK)</td><td>Você (Customer Managed Key)</td>"
                    "<td>alta, log de cada uso da key</td>"
                    "<td>Compliance (PCI/HIPAA), revogação granular</td></tr>"
                    "<tr><td>SSE-C</td><td>Você manda chave a cada request</td>"
                    "<td>nenhuma na AWS</td><td>Casos especiais</td></tr>"
                    "<tr><td>Client-side</td><td>Você criptografa antes</td>"
                    "<td>nenhuma</td><td>Zero-trust no provedor</td></tr>"
                    "</table>"
                    "<p>Em 2023, AWS habilitou SSE-S3 default em todos os buckets. Você ainda "
                    "deve <em>especificar</em> SSE-KMS com CMK para casos sensíveis.</p>"

                    "<h3>6. Versionamento + Object Lock = anti-ransomware</h3>"
                    "<p>Cenário: atacante consegue credenciais com permissão de delete em S3. "
                    "Apaga tudo. Game over?</p>"
                    "<p>Não, se você tiver:</p>"
                    "<ul>"
                    "<li><strong>Versionamento</strong>: cada PUT cria nova versão; delete "
                    "cria 'delete marker' (recuperável).</li>"
                    "<li><strong>MFA Delete</strong>: deletar versão exige MFA do root.</li>"
                    "<li><strong>Object Lock (Compliance)</strong>: nem o root pode apagar "
                    "antes do retention period. WORM (Write Once, Read Many).</li>"
                    "<li><strong>Cross-Region Replication</strong>: cópia em região "
                    "separada com bucket policy diferente.</li>"
                    "<li><strong>Cross-Account Replication</strong>: cópia em conta "
                    "separada (atacante na conta principal não alcança).</li>"
                    "</ul>"
                    "<p>Combine os 4 para defesa contra ransomware sério.</p>"

                    "<h3>7. Lifecycle: economizando 90% em logs antigos</h3>"
                    "<p>Storage classes do S3, ordenadas por preço:</p>"
                    "<table>"
                    "<tr><th>Classe</th><th>$/GB-mês</th><th>Latência</th><th>Caso</th></tr>"
                    "<tr><td>Standard</td><td>~0.023</td><td>ms</td><td>dados quentes</td></tr>"
                    "<tr><td>Standard-IA</td><td>~0.0125</td><td>ms</td><td>infrequente, "
                    "&gt;30d</td></tr>"
                    "<tr><td>Intelligent-Tiering</td><td>auto</td><td>ms</td><td>quando não "
                    "sabe o padrão de acesso</td></tr>"
                    "<tr><td>Glacier Instant</td><td>~0.004</td><td>ms</td>"
                    "<td>arquivos &gt;90d</td></tr>"
                    "<tr><td>Glacier Flexible</td><td>~0.0036</td><td>min-horas</td>"
                    "<td>backup &gt;90d</td></tr>"
                    "<tr><td>Glacier Deep Archive</td><td>~0.00099</td><td>12h</td>"
                    "<td>compliance &gt;180d</td></tr>"
                    "</table>"
                    "<p>Lifecycle rule típica para logs:</p>"
                    "<pre><code>{\n"
                    "  \"Rules\": [{\n"
                    "    \"ID\": \"logs-tiering\",\n"
                    "    \"Status\": \"Enabled\",\n"
                    "    \"Filter\": {\"Prefix\": \"logs/\"},\n"
                    "    \"Transitions\": [\n"
                    "      {\"Days\": 30,  \"StorageClass\": \"STANDARD_IA\"},\n"
                    "      {\"Days\": 90,  \"StorageClass\": \"GLACIER_IR\"},\n"
                    "      {\"Days\": 180, \"StorageClass\": \"DEEP_ARCHIVE\"}\n"
                    "    ],\n"
                    "    \"Expiration\": {\"Days\": 2555}        \n"
                    "  }]\n"
                    "}</code></pre>"
                    "<p>Cuidado com retrieval: Glacier cobra para tirar de lá. Calcule antes.</p>"

                    "<h3>8. Site estático + CloudFront: arquitetura segura</h3>"
                    "<p>Quer hospedar SPA (React, Vue) em S3 + CloudFront? <strong>Não</strong> "
                    "torne o bucket público. Use Origin Access Control (OAC):</p>"
                    "<pre><code># Bucket policy permite só CloudFront\n"
                    "{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [{\n"
                    "    \"Effect\": \"Allow\",\n"
                    "    \"Principal\": {\"Service\": \"cloudfront.amazonaws.com\"},\n"
                    "    \"Action\": \"s3:GetObject\",\n"
                    "    \"Resource\": \"arn:aws:s3:::site-bucket/*\",\n"
                    "    \"Condition\": {\n"
                    "      \"StringEquals\": {\n"
                    "        \"AWS:SourceArn\": \"arn:aws:cloudfront::123:distribution/EXXX\"\n"
                    "      }\n"
                    "    }\n"
                    "  }]\n"
                    "}</code></pre>"
                    "<p>Bucket fica privado. Apenas o distribution X consegue ler. CloudFront "
                    "serve com TLS, cache, headers de segurança.</p>"

                    "<h3>9. Logging e detecção</h3>"
                    "<ul>"
                    "<li><strong>S3 Access Logs</strong>: registra cada request, vai para "
                    "outro bucket. Útil mas atrasado (delivery em horas).</li>"
                    "<li><strong>CloudTrail Data Events</strong>: registra cada GetObject/"
                    "PutObject em CloudTrail. Caro em alta escala, habilite só em buckets "
                    "sensíveis.</li>"
                    "<li><strong>Macie</strong>: scanner de PII em buckets. Detecta CPF, "
                    "cartão, email, etc. e classifica risco.</li>"
                    "<li><strong>GuardDuty S3 Protection</strong>: detecção comportamental "
                    "(exfiltração, public bucket criado, listagem anômala).</li>"
                    "</ul>"

                    "<h3>10. Caso real: Capital One revisitado</h3>"
                    "<p>O que vazou foi obtido via <code>s3 ls</code> + "
                    "<code>s3 sync</code> usando credenciais SSRF. 700 buckets. 100M "
                    "registros. Se houvesse:</p>"
                    "<ul>"
                    "<li>Bucket policy restritiva por VPC endpoint;</li>"
                    "<li>Macie alertando volume anômalo de download;</li>"
                    "<li>GuardDuty detectando data exfil;</li>"
                    "<li>VPC sem rota direta para S3 público (via endpoint);</li>"
                    "</ul>"
                    "<p>O ataque teria sido detectado em horas, não meses.</p>"

                    "<h3>11. Anti-patterns</h3>"
                    "<ul>"
                    "<li>Bucket público sem necessidade.</li>"
                    "<li>Credenciais hardcoded em código mobile/frontend.</li>"
                    "<li>Sem versionamento.</li>"
                    "<li>Sem encryption.</li>"
                    "<li>Bucket name sequencial e adivinhável "
                    "(<code>backup-prod-1</code>, <code>backup-prod-2</code>), facilita "
                    "scan.</li>"
                    "<li>Sem lifecycle: log de 5 anos atrás em Standard.</li>"
                    "<li>Cross-account sem audit trail.</li>"
                    "<li>Object ACLs em vez de bucket policy (legado).</li>"
                    "</ul>"
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
                  ["Performance maior.",
                   "Backup automático.",
                   "Auto-scaling."],
                  "Maior parte dos vazamentos cloud nas últimas duas décadas começou em S3 público."),
                q("Presigned URL serve para:",
                  "Conceder acesso temporário a um objeto sem expor credenciais.",
                  ["Acelerar uploads.",
                   "Substituir IAM.",
                   "Renomear arquivos."],
                  "TTL curto reduz risco. Limite método e tamanho para minimizar abuso."),
                q("Versionamento em S3 ajuda em:",
                  "Recuperação após exclusão acidental ou ransomware.",
                  ["Backup financeiro.",
                   "Aumento de IOPS.",
                   "Compressão automática."],
                  "Combine com MFA Delete e Object Lock para defesa em camadas."),
                q("SSE-KMS criptografa:",
                  "Objetos em repouso usando chaves do KMS.",
                  ["Apenas o nome do arquivo.",
                   "Trânsito.",
                   "Apenas tags."],
                  "Trânsito é coberto por TLS (HTTPS). KMS adiciona granularidade, você pode "
                  "controlar quem usa cada chave."),
                q("'Block Public Access' na conta:",
                  "Garante que nenhum bucket fique exposto por engano.",
                  ["Aumenta custo.",
                   "Bloqueia o IAM.",
                   "Apaga objetos."],
                  "Quatro flags; ative as quatro a menos que tenha caso justificável de bucket público."),
                q("Lifecycle rule pode:",
                  "Mover objetos a Glacier após N dias.",
                  ["Substituir IAM.",
                   "Habilitar HTTPS.",
                   "Renomear bucket."],
                  "Reduz custo drasticamente para dados frios. Cuidado com custo de retrieval em Glacier."),
                q("Para hospedar site estático em S3:",
                  "Habilite static website hosting + use CloudFront na frente.",
                  ["Use EC2 obrigatoriamente.",
                   "Use Route53 apenas.",
                   "Use Lambda como webserver."],
                  "CloudFront + Origin Access Identity permite manter o bucket privado."),
                q("Logs de acesso ao bucket vão para:",
                  "Outro bucket configurado como destino.",
                  ["O CloudWatch só.",
                   "O console.",
                   "Nenhum lugar."],
                  "Bucket de logs deve ser separado e com policy restritiva. Considere também CloudTrail data events."),
                q("Como evitar deleção acidental?",
                  "Object Lock + versionamento + MFA Delete.",
                  ["Não criar arquivos.",
                   "Apenas IAM.",
                   "Backup local."],
                  "Object Lock em modo Compliance impede até root de apagar antes do TTL."),
                q("S3 tem garantia de durabilidade nominal de:",
                  "11 noves (99.999999999%).",
                  ["3 noves.",
                   "5 noves.",
                   "Sem garantia."],
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
                    "<h3>1. Modelo de ameaça: do que cripto protege</h3>"
                    "<p>Antes de qualquer detalhe técnico, defina o que você está "
                    "protegendo:</p>"
                    "<ul>"
                    "<li><strong>Em repouso</strong>: alguém ganha acesso ao disco/snapshot/"
                    "backup. Ex.: provedor cloud é comprometido, snapshot é roubado, disco "
                    "descartado sem wipe.</li>"
                    "<li><strong>Em trânsito</strong>: alguém intercepta o tráfego "
                    "(MITM, ISP malicioso, Wi-Fi público). TLS resolve.</li>"
                    "<li><strong>Em uso</strong>: dados na RAM enquanto sendo processados. "
                    "Cripto convencional <em>não</em> protege; precisa Confidential "
                    "Computing (Nitro Enclaves, AMD SEV, Intel SGX).</li>"
                    "</ul>"
                    "<p>O que cripto <strong>não</strong> faz:</p>"
                    "<ul>"
                    "<li>Não substitui IAM/RBAC. Se o atacante já está autenticado como "
                    "user válido, ele lê em claro.</li>"
                    "<li>Não protege contra SQL injection ou bug na app.</li>"
                    "<li>Não protege metadados (timestamps, tamanho, padrões de acesso).</li>"
                    "<li>Sem gestão de chave correta, é só caro e inútil.</li>"
                    "</ul>"

                    "<h3>2. Simétrica vs assimétrica</h3>"
                    "<table>"
                    "<tr><th></th><th>Simétrica (AES, ChaCha20)</th>"
                    "<th>Assimétrica (RSA, ECC, Ed25519)</th></tr>"
                    "<tr><td>Chave</td><td>uma só</td><td>par público + privado</td></tr>"
                    "<tr><td>Velocidade</td><td>rápida (~GB/s)</td><td>lenta (~MB/s)</td></tr>"
                    "<tr><td>Tamanho de chave</td><td>128/256 bits</td>"
                    "<td>2048-4096 bits (RSA), 256 bits (ECC)</td></tr>"
                    "<tr><td>Caso de uso</td><td>cifrar dados em volume</td>"
                    "<td>troca de chave, assinatura</td></tr>"
                    "</table>"
                    "<p>TLS combina os dois: handshake assimétrico (RSA/ECDHE) estabelece "
                    "uma chave simétrica de sessão (AES) que é usada para o tráfego.</p>"

                    "<h3>3. Algoritmos modernos vs depreciados</h3>"
                    "<table>"
                    "<tr><th>Categoria</th><th>Use</th><th>Evite</th></tr>"
                    "<tr><td>Cifra simétrica</td><td>AES-256-GCM, ChaCha20-Poly1305</td>"
                    "<td>DES, 3DES, RC4, AES-CBC sem MAC</td></tr>"
                    "<tr><td>Hash</td><td>SHA-256, SHA-3, BLAKE2/3</td>"
                    "<td>MD5, SHA-1</td></tr>"
                    "<tr><td>KDF (senha)</td><td>Argon2id, scrypt, bcrypt</td>"
                    "<td>MD5/SHA1 puro, PBKDF2 com baixo custo</td></tr>"
                    "<tr><td>Assimétrica chave</td><td>Ed25519, X25519, ECDSA P-256, RSA-3072+</td>"
                    "<td>RSA-1024, DSA</td></tr>"
                    "<tr><td>TLS</td><td>TLS 1.3 (preferível), 1.2 OK</td>"
                    "<td>TLS 1.0/1.1, SSLv3, SSLv2</td></tr>"
                    "</table>"

                    "<h3>4. KMS, gestão de chaves como serviço</h3>"
                    "<p>KMS resolve o problema crítico: <em>onde guardar a chave?</em> "
                    "Em vez de em arquivo no disco da app, fica em HSM gerenciado, com:</p>"
                    "<ul>"
                    "<li><strong>HSM</strong> (Hardware Security Module): chip dedicado, "
                    "FIPS 140-2 Level 2 ou 3. Chave nunca sai em claro.</li>"
                    "<li>API encrypt/decrypt, sua app envia plaintext e recebe ciphertext.</li>"
                    "<li>Auditoria: cada uso da chave logado em CloudTrail.</li>"
                    "<li>Rotação automática (anual em CMKs gerenciadas).</li>"
                    "<li>Revogação: deletar chave torna dados inacessíveis (com janela de "
                    "espera de 7-30 dias para reverter).</li>"
                    "<li>Cross-account: bucket em conta A criptografado por chave em "
                    "conta B (separação de poder).</li>"
                    "</ul>"

                    "<h3>5. Envelope encryption, escala</h3>"
                    "<p>Ineficiente: para cifrar 1 TB, você não chama KMS para cada bloco. "
                    "Padrão correto:</p>"
                    "<ol>"
                    "<li>Sua app pede uma <strong>data key</strong> ao KMS: ele gera uma "
                    "chave AES-256 aleatória, cifra ela com a CMK e devolve <em>ambas</em> "
                    "(plaintext + cipher).</li>"
                    "<li>App usa a plaintext key para cifrar o dado localmente (rápido).</li>"
                    "<li>App armazena junto: <code>{ciphertext_data, "
                    "encrypted_data_key}</code>. Plaintext key joga fora.</li>"
                    "<li>Para decifrar: pede ao KMS para decifrar a "
                    "<code>encrypted_data_key</code>; recebe plaintext key; usa para "
                    "decifrar.</li>"
                    "</ol>"
                    "<p>Resultado: chave 'mestre' nunca sai do HSM, mas data keys são "
                    "armazenadas com o dado. Performance + segurança.</p>"
                    "<pre><code>import boto3, os\n"
                    "from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n"
                    "\n"
                    "kms = boto3.client('kms')\n"
                    "\n"
                    "# Gerar data key\n"
                    "resp = kms.generate_data_key(KeyId='alias/my-cmk', KeySpec='AES_256')\n"
                    "plaintext_key = resp['Plaintext']\n"
                    "encrypted_key = resp['CiphertextBlob']    # armazenar com o dado\n"
                    "\n"
                    "# Cifrar com AES-GCM (autenticada)\n"
                    "aes = AESGCM(plaintext_key)\n"
                    "nonce = os.urandom(12)\n"
                    "ciphertext = aes.encrypt(nonce, b'dados sensiveis', associated_data=b'tenant-x')\n"
                    "\n"
                    "# Para decifrar:\n"
                    "plaintext_key = kms.decrypt(CiphertextBlob=encrypted_key)['Plaintext']\n"
                    "data = AESGCM(plaintext_key).decrypt(nonce, ciphertext, b'tenant-x')</code></pre>"

                    "<h3>6. TLS 1.3, o melhor jeito de fazer</h3>"
                    "<p>TLS 1.3 resolveu vários problemas antigos:</p>"
                    "<ul>"
                    "<li>Handshake em 1 RTT (vs 2 do 1.2). 0-RTT em sessão retomada.</li>"
                    "<li>Forward secrecy obrigatório (ECDHE only).</li>"
                    "<li>Cipher suites legacy removidas (RC4, MD5, SHA1, etc.).</li>"
                    "<li>Renegociação removida (era vetor de ataque).</li>"
                    "</ul>"
                    "<p>Configuração mínima de TLS 'modern' (Mozilla):</p>"
                    "<pre><code>ssl_protocols TLSv1.3;\n"
                    "ssl_prefer_server_ciphers off;\n"
                    "ssl_ciphers TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;\n"
                    "ssl_session_timeout 1d;\n"
                    "ssl_session_cache shared:SSL:10m;\n"
                    "ssl_session_tickets off;\n"
                    "ssl_stapling on;\n"
                    "ssl_stapling_verify on;\n"
                    "add_header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\" always;</code></pre>"
                    "<p>Audite com <a href='https://www.ssllabs.com/ssltest/'>SSL Labs</a>. "
                    "Mire em A+.</p>"

                    "<h3>7. mTLS, autenticação mútua</h3>"
                    "<p>TLS comum: cliente verifica servidor (via cert). mTLS: <em>servidor "
                    "também verifica cliente</em>. Caso de uso típico: comunicação serviço a "
                    "serviço dentro de mesh.</p>"
                    "<p>Cada serviço tem certificado emitido por CA interna. Em K8s, o "
                    "service mesh (Istio, Linkerd) automatiza tudo: cada Pod recebe cert "
                    "via SPIFFE, rotação a cada 24h, validação automática. Você ganha "
                    "<em>autenticação criptográfica</em> entre serviços sem mudar código "
                    "de aplicação.</p>"

                    "<h3>8. Hashing de senhas, não é encryption</h3>"
                    "<p>Hash é unidirecional: dado o hash, não dá para voltar à senha. Mas "
                    "<strong>não use SHA-256 puro</strong> para senhas, atacante com GPU "
                    "tenta bilhões/seg. Use KDF de propósito específico:</p>"
                    "<ul>"
                    "<li><strong>Argon2id</strong>: vencedor da Password Hashing Competition "
                    "2015. Memory-hard (caro de paralelizar em GPU). Ajuste parâmetros "
                    "(memory cost, iterations, parallelism).</li>"
                    "<li><strong>bcrypt</strong>: clássico, ainda OK. Cost factor &gt; 12.</li>"
                    "<li><strong>scrypt</strong>: memory-hard como Argon2.</li>"
                    "</ul>"
                    "<pre><code>from argon2 import PasswordHasher\n"
                    "ph = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)\n"
                    "hashed = ph.hash('senha-do-usuario')\n"
                    "# salva 'hashed' no banco\n"
                    "ph.verify(hashed, 'senha-do-usuario')</code></pre>"
                    "<p>Sempre adicione <strong>salt</strong> (Argon2 e bcrypt fazem "
                    "automaticamente). Sem salt, rainbow tables resolvem.</p>"

                    "<h3>9. Post-quantum: o que vem aí</h3>"
                    "<p>Computadores quânticos com qubits suficientes vão quebrar RSA e ECC "
                    "via algoritmo de Shor. Estimativa atual: 10-20 anos. Mas dados "
                    "criptografados <em>hoje</em> e capturados podem ser decifrados "
                    "<em>amanhã</em> (harvest now, decrypt later).</p>"
                    "<p>NIST publicou em 2024 os primeiros padrões post-quantum: ML-KEM "
                    "(Kyber, troca de chave) e ML-DSA (Dilithium, assinatura). Cloudflare, "
                    "Google e AWS já oferecem TLS híbrido (clássico + post-quantum) opcional. "
                    "Comece a olhar agora se seus dados têm valor por &gt;10 anos.</p>"

                    "<h3>10. Caso real: ROCA, chaves quebradas em massa</h3>"
                    "<p>Em 2017, descobriu-se que uma biblioteca da Infineon (usada em smart "
                    "cards e TPMs) gerava chaves RSA-2048 com fraqueza matemática que "
                    "permitia fatoração com ~US$ 38k de cloud. Resultado: chaves de governos "
                    "(Estônia), corporações e milhões de smart cards tiveram que ser "
                    "rotacionadas. Lições:</p>"
                    "<ul>"
                    "<li>Tamanho de chave não basta, implementação importa.</li>"
                    "<li>Use libs auditadas (OpenSSL, libsodium, BoringSSL).</li>"
                    "<li>Mecanismos de rotação devem existir desde o dia 1.</li>"
                    "<li>HSM com firmware atualizável é vantagem.</li>"
                    "</ul>"

                    "<h3>11. Anti-patterns</h3>"
                    "<ul>"
                    "<li>Senha em SHA-256 sem salt nem KDF.</li>"
                    "<li>Chave estática hard-coded no código.</li>"
                    "<li>TLS com cert auto-assinado em produção.</li>"
                    "<li>Versão de OpenSSL desatualizada (CVEs antigas).</li>"
                    "<li>HSTS sem includeSubDomains, sem preload.</li>"
                    "<li>Cifra simétrica sem autenticação (AES-CBC sem MAC).</li>"
                    "<li>IV/nonce reusado.</li>"
                    "<li>Encryption at rest sem encryption at trânsito (faz pouco sentido).</li>"
                    "<li>'Encriptamos os dados' mas a chave fica no mesmo disco.</li>"
                    "</ul>"
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
                  ["Apenas DNS.", "Apenas IP.", "Apenas firewall."],
                  "Cliente verifica o certificado contra CAs confiáveis; servidor prova posse da chave privada."),
                q("Por que rotacionar chaves KMS?",
                  "Reduz impacto de eventual comprometimento.",
                  ["Aumenta velocidade.", "Reduz custo.", "Necessário para HTTP."],
                  "KMS rotaciona automaticamente em CMKs gerenciadas (anual). Re-criptografa lazy ao acessar."),
                q("HSM serve para:",
                  "Armazenar chaves criptográficas em hardware dedicado.",
                  ["Substituir IAM.", "Criar políticas.", "Comprimir dados."],
                  "HSMs têm certificações (FIPS 140-3 Level 3) e impedem extração da chave."),
                q("Algoritmo recomendado para hash de senha:",
                  "Argon2 ou bcrypt com custo alto.",
                  ["MD5.", "SHA-1.", "Base64."],
                  "Argon2 ganhou a Password Hashing Competition. bcrypt continua aceitável."),
                q("Forward secrecy garante:",
                  "Que comprometimento da chave atual não revele tráfego antigo.",
                  ["Backup automático.",
                   "Velocidade maior.",
                   "Compatibilidade SSLv2."],
                  "ECDHE gera chave de sessão efêmera. Sem forward secrecy, atacante guarda tráfego "
                  "para descriptografar quando obtiver a chave."),
                q("HSTS é mecanismo de:",
                  "Força HTTPS em browsers.",
                  ["Cripto em repouso.",
                   "Backup.",
                   "Roteamento."],
                  "Header HTTP que diz: 'sempre acesse este host por HTTPS pelos próximos N segundos'."),
                q("Certificate Authority (CA) confiável é necessária para:",
                  "Que clientes confiem no certificado sem warning.",
                  ["Aumentar performance.",
                   "Comprimir dados.",
                   "Servir HTTP."],
                  "Em produção pública use Let's Encrypt/ACM/etc. Em interno, considere CA privada (Vault, AWS PCA)."),
                q("Vazou a chave privada do TLS, deve-se:",
                  "Revogar e rotacionar imediatamente.",
                  ["Manter por compatibilidade.",
                   "Apagar logs antigos.",
                   "Abrir SLA."],
                  "Tráfego antigo pode ser descriptografado se não houver forward secrecy. Revogue via CRL/OCSP."),
                q("'Encryption at rest' protege:",
                  "Dados armazenados em disco.",
                  ["Apenas em RAM.",
                   "Tráfego entre servidores.",
                   "Apenas DNS."],
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
                  ["CPU, RAM, disco, rede.",
                   "Reqs/s, fps, mb, ms.",
                   "Up/down apenas."],
                  "Definidos pelo Google SRE Book. Cobrem as dimensões essenciais de qualquer serviço."),
                q("SLO mede:",
                  "Objetivo de qualidade de serviço (ex.: 99,9% de disponibilidade).",
                  ["Custo de cloud.",
                   "Bug count.",
                   "Latência única."],
                  "É o objetivo interno; SLA é o contrato com cliente (geralmente mais conservador)."),
                q("Diferença SLI vs SLO:",
                  "SLI é a medida (indicador), SLO é o objetivo.",
                  ["São sinônimos.",
                   "SLI é contrato com cliente.",
                   "SLO é métrica bruta."],
                  "Você mede SLI; SLO é o limite que diz se está bom ou ruim."),
                q("Por que alarme em SLO em vez de threshold:",
                  "Refletem o que importa para o usuário, não números arbitrários.",
                  ["Reduzem custo.",
                   "Substituem logs.",
                   "Habilitam HTTPS."],
                  "Burn rate alerta quando o orçamento de erro está sendo consumido rápido, sinal real, não ruído."),
                q("PromQL é linguagem de:",
                  "Consulta do Prometheus.",
                  ["Python para alarmes.",
                   "Logs estruturados.",
                   "JSON."],
                  "Permite agregações, taxas (`rate(...)[5m]`), percentis (`histogram_quantile`)."),
                q("Histograma em métricas serve para:",
                  "Distribuir valores em buckets e calcular percentis (p99 etc.).",
                  ["Contar reqs.",
                   "Listar erros.",
                   "Substituir traces."],
                  "Histograma é local (cliente). Para somar entre instâncias, use buckets compatíveis."),
                q("Alert fadiga ocorre quando:",
                  "Há tantos alertas que ninguém presta atenção.",
                  ["O Prometheus cai.",
                   "O Grafana atualiza.",
                   "O SLA aumenta."],
                  "Cada alerta sem ação útil corrói a confiança no sistema. Limpe agressivamente."),
                q("Métrica vs log vs trace:",
                  "Métrica é numérica agregada; log é evento; trace é fluxo distribuído.",
                  ["São a mesma coisa.",
                   "Apenas trace importa.",
                   "Métrica = trace."],
                  "Os três são pilares da observabilidade, complementares, não substitutos."),
                q("SLO de 99,99% permite quantos minutos de downtime/mês?",
                  "Cerca de 4,3 minutos.",
                  ["Cerca de 1 hora.",
                   "0 minutos.",
                   "Cerca de 1 dia."],
                  "30d x 24h x 60min x 0,01% ≈ 4,3 min. Quatro noves é caro."),
                q("Cardinalidade alta em métricas causa:",
                  "Custo crescente e degradação do backend.",
                  ["Aceleração.",
                   "Auto-resolução.",
                   "Backup."],
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
                    "<h3>1. RPO e RTO, as duas métricas-base</h3>"
                    "<p><strong>RPO</strong> (Recovery Point Objective): quanto de dado é "
                    "aceitável perder. Se RPO = 1h, você precisa ter backup ou replicação "
                    "que garanta dados no máximo 1h atrasados.</p>"
                    "<p><strong>RTO</strong> (Recovery Time Objective): em quanto tempo o "
                    "serviço deve voltar. Se RTO = 30min, manualidade está fora de questão.</p>"
                    "<p>Calcule por aplicação:</p>"
                    "<table>"
                    "<tr><th>App</th><th>RPO</th><th>RTO</th><th>Estratégia</th></tr>"
                    "<tr><td>Marketing site (estático)</td><td>24h</td><td>4h</td>"
                    "<td>backup &amp; restore</td></tr>"
                    "<tr><td>Blog interno</td><td>24h</td><td>8h</td>"
                    "<td>backup diário</td></tr>"
                    "<tr><td>App SaaS pequena</td><td>1h</td><td>1h</td>"
                    "<td>pilot light multi-region</td></tr>"
                    "<tr><td>E-commerce</td><td>5min</td><td>30min</td>"
                    "<td>warm standby</td></tr>"
                    "<tr><td>Trading platform</td><td>0</td><td>&lt;5min</td>"
                    "<td>active-active multi-region</td></tr>"
                    "</table>"

                    "<h3>2. Regra 3-2-1 (e variações modernas)</h3>"
                    "<p>Regra clássica:</p>"
                    "<ul>"
                    "<li><strong>3</strong> cópias dos dados (1 produção + 2 backups).</li>"
                    "<li>Em <strong>2</strong> mídias diferentes (não só disco).</li>"
                    "<li>Com <strong>1</strong> offsite (outra região, outra cloud, outra "
                    "empresa).</li>"
                    "</ul>"
                    "<p>Modernização <strong>3-2-1-1-0</strong>:</p>"
                    "<ul>"
                    "<li>+1 cópia <strong>imutável</strong> (Object Lock, WORM).</li>"
                    "<li>0 erros após teste de restore.</li>"
                    "</ul>"
                    "<p>A imutabilidade é resposta direta a ransomware: atacantes hoje "
                    "atacam backups primeiro. Cópia que não pode ser apagada nem pelo root "
                    "&mdash; só com retention period &mdash; sobrevive.</p>"

                    "<h3>3. Estratégias de DR, quanto custo, quanto tempo</h3>"
                    "<table>"
                    "<tr><th>Estratégia</th><th>RTO típico</th><th>Custo</th><th>Quando usar</th></tr>"
                    "<tr><td>Backup &amp; restore</td><td>horas</td><td>baixo</td>"
                    "<td>apps tolerantes a downtime</td></tr>"
                    "<tr><td>Pilot light</td><td>30-60min</td><td>baixo-médio</td>"
                    "<td>infra mínima ligada na região DR (DB replicando)</td></tr>"
                    "<tr><td>Warm standby</td><td>5-30min</td><td>médio-alto</td>"
                    "<td>ambiente DR rodando reduzido, escala em caso</td></tr>"
                    "<tr><td>Multi-site active-active</td><td>&lt;5min</td><td>2x+</td>"
                    "<td>tráfego distribuído entre regiões em produção</td></tr>"
                    "</table>"
                    "<p>Não existe almoço grátis: RTO menor = custo maior + complexidade "
                    "maior. Escolha por aplicação, não global.</p>"

                    "<h3>4. Snapshots ≠ backup</h3>"
                    "<p>EBS snapshot incremental no provedor é cômodo, mas:</p>"
                    "<ul>"
                    "<li>Vive na mesma conta. Conta comprometida = snapshot apagado.</li>"
                    "<li>Vive na mesma região (snapshots base). Falha de região = "
                    "perdido.</li>"
                    "<li>Sem object-lock por padrão.</li>"
                    "</ul>"
                    "<p>Backup verdadeiro vai para:</p>"
                    "<ul>"
                    "<li>Outra <em>conta</em> (cross-account replication, IAM separada).</li>"
                    "<li>Outra <em>região</em> (cross-region copy).</li>"
                    "<li>Outro <em>provedor</em> (AWS → Wasabi, ou backup local).</li>"
                    "<li>Com <strong>retention</strong> imutável.</li>"
                    "</ul>"

                    "<h3>5. Ransomware-resistant backup</h3>"
                    "<p>Atacantes modernos seguem playbook:</p>"
                    "<ol>"
                    "<li>Comprometem credencial em phishing.</li>"
                    "<li>Mapeiam ambiente (active directory, cloud).</li>"
                    "<li><strong>Apagam ou criptografam backups</strong>.</li>"
                    "<li>Criptografam dados de produção.</li>"
                    "<li>Pedem resgate.</li>"
                    "</ol>"
                    "<p>Defesas em camada:</p>"
                    "<ul>"
                    "<li><strong>Object Lock Compliance</strong>: nem o root pode apagar.</li>"
                    "<li><strong>MFA Delete</strong>: deleção de versão exige MFA root.</li>"
                    "<li><strong>Conta separada</strong>: credenciais de produção não "
                    "alcançam conta de backup.</li>"
                    "<li><strong>Air gap lógico</strong>: backup em provider diferente, "
                    "credenciais separadas.</li>"
                    "<li><strong>Air gap físico</strong>: tape offline (clássico, ainda "
                    "válido para tier final).</li>"
                    "<li><strong>Imutability period</strong>: 90+ dias para detectar "
                    "compromisso silencioso.</li>"
                    "</ul>"

                    "<h3>6. Backup de banco de dados, não é só copy</h3>"
                    "<p>Bancos transacionais precisam consistência:</p>"
                    "<ul>"
                    "<li><strong>Cold backup</strong>: parar o banco, copiar arquivo. "
                    "Simples mas downtime.</li>"
                    "<li><strong>Hot backup</strong>: <code>pg_basebackup</code> em "
                    "Postgres, <code>mysqldump --single-transaction</code> em MySQL, usa "
                    "snapshot de transação para consistência.</li>"
                    "<li><strong>WAL/binlog archiving</strong>: PITR (point-in-time "
                    "recovery). Backup base + WAL contínuo permite restaurar para qualquer "
                    "segundo.</li>"
                    "<li><strong>Logical backup</strong> (pg_dump): mais lento mas "
                    "portável (versões diferentes, schemas).</li>"
                    "</ul>"
                    "<p>RDS faz tudo isso automaticamente: backup automático com retenção "
                    "configurável, PITR para qualquer segundo dos últimos 35 dias, snapshots "
                    "manuais. Configure mas <em>teste o restore</em>.</p>"

                    "<h3>7. Game days, o teste que separa plano de ficção</h3>"
                    "<p>Plano só vale se foi testado. Game day: simulação real do que você "
                    "espera que o time faça. Exemplos:</p>"
                    "<ul>"
                    "<li>Mata a região primária via Fault Injection Simulator.</li>"
                    "<li>Apaga (em ambiente isolado) o banco principal e cronometre o "
                    "restore.</li>"
                    "<li>Quebra DNS, rede, certificados.</li>"
                    "<li>Engenheiro 'de plantão' age sem ajuda; resto observa.</li>"
                    "</ul>"
                    "<p>Métricas a coletar:</p>"
                    "<ul>"
                    "<li>Tempo até detecção real.</li>"
                    "<li>Tempo até decisão de failover.</li>"
                    "<li>Tempo de restore.</li>"
                    "<li>Quem teve que ser acordado.</li>"
                    "<li>Documentação que faltava.</li>"
                    "</ul>"
                    "<p>Frequência: trimestral em apps tier-1; anual em tier-2. "
                    "Ferramentas: AWS FIS, Chaos Mesh, Litmus, Gremlin, custom.</p>"

                    "<h3>8. Caso real: GitLab 2017, anatomia da limpa</h3>"
                    "<p>Em 31/jan/2017, engenheiro do GitLab tentou limpar uma replicação "
                    "do banco principal. Por engano, rodou <code>rm -rf</code> no "
                    "<em>banco principal</em> (não na réplica). 300 GB de dados deletados.</p>"
                    "<p>Eles tinham 5 mecanismos de backup. Quando foram restaurar:</p>"
                    "<ol>"
                    "<li>S3 backup automático: <strong>desligado há meses</strong> (config "
                    "errada não detectada).</li>"
                    "<li>Daily snapshots LVM: <strong>último era de 24h atrás</strong> e "
                    "demorava 18h para restaurar.</li>"
                    "<li>Azure disk snapshot: <strong>nunca ativado</strong>.</li>"
                    "<li>Replication para staging: <strong>ativa, mas atrás 6h</strong>.</li>"
                    "<li>Backup pg_dump: <strong>arquivo de 0 bytes, backup quebrado</strong>.</li>"
                    "</ol>"
                    "<p>Recuperaram do snapshot LVM com 6h de perda de dados (alguns issues, "
                    "MRs perdidos). Live-streamed o postmortem como honestidade.</p>"
                    "<p>Lições documentadas:</p>"
                    "<ul>"
                    "<li>5 mecanismos de backup, 4 não funcionavam. <em>Teste teste teste.</em></li>"
                    "<li>Monitoramento de backup: 'backup não rodou há 24h' deveria ser "
                    "alerta vermelho.</li>"
                    "<li>Engenheiro fadigado às 23h, fadiga é fator de incidente.</li>"
                    "<li>Hostname ambíguo facilitou o erro (db1 vs db2).</li>"
                    "</ul>"

                    "<h3>9. 'Backup is not done until you've tested restore'</h3>"
                    "<p>Mensalmente / trimestralmente, em ambiente isolado:</p>"
                    "<ol>"
                    "<li>Provisione recurso novo (DB, S3, instance).</li>"
                    "<li>Restore o backup mais recente.</li>"
                    "<li>Verifique integridade: schema, contagem de rows, queries de "
                    "smoke test.</li>"
                    "<li>Cronometre tempo total.</li>"
                    "<li>Compare com seu RTO documentado.</li>"
                    "<li>Documente desvios e ajuste.</li>"
                    "</ol>"
                    "<p>Automatize esse processo: AWS Backup tem 'restore testing'. "
                    "Pipelines em Terraform podem provisionar/restaurar/validar/destruir.</p>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li>Snapshot na mesma conta = backup.</li>"
                    "<li>Não testar restore.</li>"
                    "<li>Backup só de banco, não de configuração/secrets.</li>"
                    "<li>Não criptografar backup (vazou backup, vazou tudo).</li>"
                    "<li>Retenção sem cap (backup de 5 anos virando custo top-3).</li>"
                    "<li>Sem RTO/RPO documentado por aplicação.</li>"
                    "<li>Plano DR existe, mas equipe nunca executou.</li>"
                    "<li>Backup em região vizinha ('us-east-1' e 'us-east-2'), desastre "
                    "geo-correlacionado pode pegar as duas.</li>"
                    "</ul>"
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
                    "<h3>1. Por que FinOps existe</h3>"
                    "<p>Em on-prem, comprar hardware era decisão de comitê: 6 meses de "
                    "discussão, capex, contrato. Você pensava muito antes.</p>"
                    "<p>Em cloud, qualquer dev provisiona EC2 com um clique. Velocidade "
                    "aumenta, mas decisões de custo se distribuem para centenas de pessoas. "
                    "Sem framework, vira o oposto: muitas decisões pequenas e ruins somando "
                    "fatura mensal absurda.</p>"
                    "<p>FinOps não é cortar custo. É <em>tomar boas decisões com dados de "
                    "custo</em>, às vezes a decisão certa é gastar mais (escalar para "
                    "atender Black Friday). O ponto é estar consciente.</p>"

                    "<h3>2. Visibilidade primeiro: tagging strategy</h3>"
                    "<p>Sem tags, você sabe que paga US$ 50k/mês mas não sabe quem usa. "
                    "Padrão recomendado: defina tags <em>obrigatórias</em> para todo "
                    "recurso:</p>"
                    "<table>"
                    "<tr><th>Tag</th><th>Exemplo</th><th>Para quê</th></tr>"
                    "<tr><td><code>Environment</code></td><td>prod, staging, dev</td>"
                    "<td>separar custo por ambiente</td></tr>"
                    "<tr><td><code>Owner</code></td><td>team-payments@</td>"
                    "<td>quem responde se algo sumir</td></tr>"
                    "<tr><td><code>CostCenter</code></td><td>CC-1234</td>"
                    "<td>chargeback contábil</td></tr>"
                    "<tr><td><code>Project</code></td><td>checkout-redesign</td>"
                    "<td>ROI por projeto</td></tr>"
                    "<tr><td><code>ManagedBy</code></td><td>terraform, manual</td>"
                    "<td>identificar drift</td></tr>"
                    "<tr><td><code>ExpiresAt</code></td><td>2026-12-31</td>"
                    "<td>recursos temporários</td></tr>"
                    "</table>"
                    "<p>Imponha via SCP/Org Policy: 'recurso sem tag obrigatória, deny "
                    "create'. Ative <em>cost allocation tags</em> em AWS Billing (uma vez "
                    "ativada, vira filtro no Cost Explorer).</p>"

                    "<h3>3. Modelos de cobrança em AWS (e equivalentes)</h3>"
                    "<table>"
                    "<tr><th>Modelo</th><th>Desconto</th><th>Compromisso</th><th>Quando</th></tr>"
                    "<tr><td>On-demand</td><td>0%</td><td>nenhum</td>"
                    "<td>desenvolvimento, picos imprevisíveis</td></tr>"
                    "<tr><td>Reserved Instance (1y)</td><td>até 40%</td><td>1 ano, type fixo</td>"
                    "<td>baseline previsível</td></tr>"
                    "<tr><td>Reserved Instance (3y)</td><td>até 60%</td><td>3 anos, type fixo</td>"
                    "<td>workload core estável</td></tr>"
                    "<tr><td>Savings Plans</td><td>até 70%</td>"
                    "<td>1-3 anos, US$/h flexível em type/region</td>"
                    "<td>baseline mas com flexibilidade</td></tr>"
                    "<tr><td>Spot Instance</td><td>até 90%</td>"
                    "<td>nenhum, pode ser interrompida com 2min de aviso</td>"
                    "<td>batch, CI, ML training, workload tolerante</td></tr>"
                    "</table>"
                    "<p>Estratégia típica em produção:</p>"
                    "<ul>"
                    "<li>~70% baseline em Savings Plans (compute + Lambda + Fargate).</li>"
                    "<li>~20% em Spot para workloads tolerantes.</li>"
                    "<li>~10% on-demand para picos imprevisíveis.</li>"
                    "</ul>"

                    "<h3>4. Right-sizing, a maioria das instâncias está superprovisionada</h3>"
                    "<p>Análise típica em ambientes maduros: 30-50% das EC2 têm "
                    "<em>CPU médio &lt; 10%</em> sustentado. Você está pagando por capacidade "
                    "que não usa.</p>"
                    "<p>Ferramentas recomendam:</p>"
                    "<ul>"
                    "<li><strong>AWS Compute Optimizer</strong>: olha métricas "
                    "CloudWatch/CloudWatch Agent e sugere instances menores.</li>"
                    "<li><strong>Azure Advisor</strong>: equivalente.</li>"
                    "<li><strong>GCP Recommender</strong>: idem.</li>"
                    "</ul>"
                    "<p>Estratégias:</p>"
                    "<ul>"
                    "<li>Trocar família: <code>m6i</code> (general) → <code>t3</code> (burst) "
                    "para apps com tráfego variável.</li>"
                    "<li>Reduzir tamanho: <code>m6i.2xlarge</code> → <code>m6i.large</code> "
                    "se CPU médio &lt; 30%.</li>"
                    "<li>Migrar para Graviton (ARM): mesmo desempenho, ~20% mais barato. "
                    "<code>m6g</code>, <code>c7g</code>, etc. Recompila ou usa imagem "
                    "multi-arch.</li>"
                    "<li>Para cargas variáveis: serverless (Lambda, Fargate, Cloud Run) "
                    "escala a zero.</li>"
                    "</ul>"

                    "<h3>5. Recursos órfãos, o ralo silencioso</h3>"
                    "<p>Em qualquer conta &gt; 6 meses, há:</p>"
                    "<ul>"
                    "<li>EBS volumes desanexados (instância foi deletada, volume ficou).</li>"
                    "<li>Snapshots de anos atrás.</li>"
                    "<li>Elastic IPs não associados (US$ 0.005/h cada).</li>"
                    "<li>NAT Gateways esquecidos em VPCs sem tráfego.</li>"
                    "<li>RDS em <code>stopped</code> (cobrança continua de storage).</li>"
                    "<li>S3 buckets com data lake gigante de POC abandonada.</li>"
                    "<li>CloudWatch logs sem retention (cresce indefinidamente).</li>"
                    "<li>Load balancers sem target.</li>"
                    "<li>Lambdas com retention de log infinito.</li>"
                    "</ul>"
                    "<p>Em ambientes grandes, isso vira 5-15% da fatura. Auditoria "
                    "automatizada com <strong>Cloud Custodian</strong> funciona muito bem:</p>"
                    "<pre><code># custodian.yml\n"
                    "policies:\n"
                    "  - name: ebs-unattached-old\n"
                    "    resource: ebs\n"
                    "    filters:\n"
                    "      - State: available           # desanexado\n"
                    "      - type: value\n"
                    "        key: CreateTime\n"
                    "        op: less-than\n"
                    "        value_type: age\n"
                    "        value: 30\n"
                    "    actions:\n"
                    "      - type: tag\n"
                    "        tags:\n"
                    "          'cleanup': 'pending'\n"
                    "      - type: notify\n"
                    "        to: ['platform@example.com']</code></pre>"
                    "<p>Após review do dono, segunda passada deleta de fato.</p>"

                    "<h3>6. Auto-scaling como FinOps</h3>"
                    "<p>Provisionar para o pico = pagar pico o tempo todo. Auto-scaling "
                    "ajusta dinamicamente:</p>"
                    "<ul>"
                    "<li><strong>EC2 Auto Scaling Groups</strong>: target tracking (ex.: "
                    "manter CPU médio em 60%).</li>"
                    "<li><strong>K8s HPA</strong> (Horizontal Pod Autoscaler): scale "
                    "Pods baseado em métricas custom.</li>"
                    "<li><strong>K8s Cluster Autoscaler</strong> ou <strong>Karpenter</strong>: "
                    "adiciona/remove nodes baseado em pending pods.</li>"
                    "<li><strong>Lambda</strong>: escala a zero quando ninguém chama.</li>"
                    "<li><strong>Fargate</strong>: paga só pelo container, escala 0-N.</li>"
                    "</ul>"
                    "<p>Karpenter (em K8s) é particularmente impressionante: provisiona node "
                    "exato pro pod (Spot quando possível, certifica family/size por "
                    "workload), economia substancial vs Cluster Autoscaler clássico.</p>"

                    "<h3>7. Egress, NAT Gateway, e os custos invisíveis</h3>"
                    "<p>Custos que matam silenciosamente:</p>"
                    "<table>"
                    "<tr><th>Item</th><th>$/unidade</th><th>Estimativa de impacto</th></tr>"
                    "<tr><td>Tráfego saindo da AWS</td><td>~$0.09/GB</td>"
                    "<td>app que serve vídeo: $$$</td></tr>"
                    "<tr><td>Tráfego cross-region</td><td>~$0.02/GB</td>"
                    "<td>replicação descuidada</td></tr>"
                    "<tr><td>Tráfego cross-AZ</td><td>~$0.01/GB</td>"
                    "<td>app em K8s sem topology aware routing</td></tr>"
                    "<tr><td>NAT Gateway</td><td>~$32/mês + $0.045/GB</td>"
                    "<td>privada → internet caro</td></tr>"
                    "<tr><td>VPC Endpoint Interface</td><td>~$7/mês por AZ</td>"
                    "<td>caro em escala mas pode valer</td></tr>"
                    "</table>"
                    "<p>Mitigações:</p>"
                    "<ul>"
                    "<li>VPC Endpoint Gateway (S3, DynamoDB), gratuito.</li>"
                    "<li>CloudFront para egress (cobra menos por GB).</li>"
                    "<li>Compressão (gzip, brotli) em respostas HTTP.</li>"
                    "<li>Cache em borda.</li>"
                    "<li>Topology-aware service em K8s (mesma AZ first).</li>"
                    "</ul>"

                    "<h3>8. Budgets, alertas e quotas</h3>"
                    "<p>Configure ANTES do primeiro deploy:</p>"
                    "<pre><code>resource \"aws_budgets_budget\" \"monthly\" {\n"
                    "  name         = \"prod-monthly\"\n"
                    "  budget_type  = \"COST\"\n"
                    "  limit_amount = \"5000\"\n"
                    "  limit_unit   = \"USD\"\n"
                    "  time_unit    = \"MONTHLY\"\n"
                    "  \n"
                    "  notification {\n"
                    "    comparison_operator = \"GREATER_THAN\"\n"
                    "    threshold           = 50\n"
                    "    threshold_type      = \"PERCENTAGE\"\n"
                    "    notification_type   = \"FORECASTED\"\n"
                    "    subscriber_email_addresses = [\"finance@example.com\"]\n"
                    "  }\n"
                    "  notification {\n"
                    "    comparison_operator = \"GREATER_THAN\"\n"
                    "    threshold           = 90\n"
                    "    notification_type   = \"ACTUAL\"\n"
                    "    subscriber_email_addresses = [\"oncall@example.com\"]\n"
                    "  }\n"
                    "}</code></pre>"
                    "<p>Em conta de sandbox, considere AWS Budget Action: 'aplica SCP de "
                    "deny EC2 RunInstances quando atingir 100%'. Evita explosão.</p>"

                    "<h3>9. Cultura FinOps: Crawl / Walk / Run</h3>"
                    "<p>FinOps Foundation define maturity:</p>"
                    "<ul>"
                    "<li><strong>Crawl</strong>: visibilidade básica. Tags, Cost Explorer, "
                    "budgets. KPIs simples.</li>"
                    "<li><strong>Walk</strong>: otimização contínua. Right-sizing automatizado. "
                    "Showback por equipe. Anomaly detection (Cost Anomaly).</li>"
                    "<li><strong>Run</strong>: decisões de produto influenciadas por custo. "
                    "Chargeback. Forecasting integrado a planning. Unit economics "
                    "(<code>$ / transação</code>).</li>"
                    "</ul>"
                    "<p>Não pule etapas. Sem visibilidade básica, qualquer 'otimização' é "
                    "torcida.</p>"

                    "<h3>10. Caso real: Fly.io e a fatura inesperada</h3>"
                    "<p>Em 2024, Fly.io publicou postmortem público: cliente teve crash "
                    "loop em VM levando a 50TB de transferência cross-region em 2 dias. "
                    "Fatura projetada: US$ 70k. Lições documentadas:</p>"
                    "<ul>"
                    "<li>Cliente tinha budget mas nunca configurou alerta.</li>"
                    "<li>Loop demorou 18h para ser detectado pelo time.</li>"
                    "<li>Fly absorveu 80% do custo (boa relação).</li>"
                    "<li>Lição da Fly: rate-limit de egress por padrão em novas contas.</li>"
                    "<li>Lição do cliente: alarme em 'tráfego/min &gt; X' = caro vir do "
                    "nada.</li>"
                    "</ul>"

                    "<h3>11. Anti-patterns</h3>"
                    "<ul>"
                    "<li>Comprar Reserved 3-year sem analisar uso.</li>"
                    "<li>Não usar tag, todo recurso é 'misc'.</li>"
                    "<li>Sem retention em CloudWatch Logs.</li>"
                    "<li>Snapshot diário de tudo, sem expiração.</li>"
                    "<li>Provisionar instance grande 'para garantir' sem medir.</li>"
                    "<li>Spot em workload stateful sem checkpoint.</li>"
                    "<li>Sem alerta de anomalia (Cost Anomaly Detection é grátis em AWS).</li>"
                    "<li>Time financeiro sem acesso a Cost Explorer.</li>"
                    "<li>Showback que ninguém olha.</li>"
                    "</ul>"
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
