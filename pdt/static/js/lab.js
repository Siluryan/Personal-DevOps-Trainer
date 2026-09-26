/**
 * Laboratório prático interativo — 5 formatos, todos por toque (sem
 * digitar, sem arrastar): terminal (montar comando por token), find_flaw
 * (achar a linha errada), order (ordenar etapa), blanks (completar config)
 * e scenario (decisão com consequência).
 *
 * Deliberadamente client-side: não executa comando de verdade. A t4g.nano
 * que roda a plataforma não comporta sandbox por aluno, e digitar comando
 * de terminal no celular é inviável — então o lab valida RACIOCÍNIO, não
 * sintaxe de shell. Ver docstring de apps.courses.models.Lab.
 *
 * commandsEquivalent espelha apps/courses/command_equiv.py: mesma ordem
 * de posicionais e as mesmas flags. Em dig/journalctl/kubectl/syft a
 * flag pode mudar de lugar; em docker/git/sudo/pre-commit ela tem de
 * ficar no mesmo vão, senão o comando muda de sentido.
 */
var LAB_VALUED_FLAGS = {
  "-eo": 1, "-perm": 1, "-type": 1, "-name": 1, "-m": 1, "-p": 1, "-S": 1,
  "-n": 1, "-o": 1, "-t": 1, "-b": 1, "-u": 1, "-f": 1, "-c": 1,
  "--severity": 1, "--exit-code": 1, "--name": 1, "--network": 1,
  "--shell": 1, "--home-dir": 1, "--namespace": 1, "--publish-url": 1,
};
var LAB_STICKY_BINS = { docker: 1, git: 1, sudo: 1, "pre-commit": 1 };

function labIsFlag(token) {
  return (token.charAt(0) === "-" || token.charAt(0) === "+") && token !== "-" && token !== "--";
}

function labScan(tokens) {
  var pos = [];
  var gaps = [[]];
  for (var i = 0; i < tokens.length; i++) {
    var tok = tokens[i];
    if (labIsFlag(tok)) {
      if (LAB_VALUED_FLAGS[tok] && i + 1 < tokens.length) {
        gaps[gaps.length - 1].push(tok + "\0" + tokens[i + 1]);
        i++;
        continue;
      }
      gaps[gaps.length - 1].push(tok);
      continue;
    }
    pos.push(tok);
    gaps.push([]);
  }
  return { pos: pos, gaps: gaps };
}

function commandsEquivalent(left, right) {
  if (!left || !right || !left.length || !right.length) return false;
  if (left[0] !== right[0]) return false;
  var a = labScan(left.slice(1));
  var b = labScan(right.slice(1));
  if (a.pos.join("\0") !== b.pos.join("\0")) return false;
  if (LAB_STICKY_BINS[left[0]]) {
    if (a.gaps.length !== b.gaps.length) return false;
    for (var i = 0; i < a.gaps.length; i++) {
      if (a.gaps[i].slice().sort().join("\0") !== b.gaps[i].slice().sort().join("\0")) return false;
    }
    return true;
  }
  var fa = [];
  var fb = [];
  a.gaps.forEach(function (gap) { fa = fa.concat(gap); });
  b.gaps.forEach(function (gap) { fb = fb.concat(gap); });
  return fa.sort().join("\0") === fb.sort().join("\0");
}

function labState(labId, kind, spec, alreadyDone, completeUrl) {
  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.content || "";
  const shuffle = (arr) => {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  const base = {
    labId,
    kind,
    spec,
    done: alreadyDone,
    checked: false,
    correct: false,

    async markComplete() {
      if (this.done) return;
      this.done = true;
      try {
        await fetch(completeUrl, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
        });
      } catch (e) {
        // sem rede: mantém o "concluído" local, o próximo POST bem-sucedido
        // (em qualquer lab) já teria sincronizado; não é crítico travar aqui.
      }
    },
  };

  if (kind === "terminal") {
    return {
      ...base,
      pool: shuffle([...spec.correct_command, ...(spec.distractor_tokens || [])]),
      chosen: [],
      pick(index) {
        if (this.checked && this.correct) return;
        this.chosen.push(this.pool[index]);
        this.pool.splice(index, 1);
        this.checked = false;
      },
      undo() {
        if (this.checked && this.correct) return;
        if (!this.chosen.length) return;
        this.pool.push(this.chosen.pop());
        this.checked = false;
      },
      check() {
        this.checked = true;
        // Só conta ordem que é o mesmo comando que o gabarito. Uma
        // accepted_commands inválida (flag separada do valor) não passa.
        var answers = [spec.correct_command].concat(spec.accepted_commands || []);
        var got = this.chosen;
        this.correct = answers.some(function (cmd) {
          return commandsEquivalent(spec.correct_command, cmd) && commandsEquivalent(cmd, got);
        });
        if (this.correct) this.markComplete();
      },
    };
  }

  if (kind === "find_flaw") {
    return {
      ...base,
      selected: null,
      select(i) {
        if (this.checked && this.correct) return;
        this.selected = i;
        this.checked = false;
      },
      check() {
        if (this.selected === null) return;
        this.checked = true;
        this.correct = this.selected === spec.flaw_line_index;
        if (this.correct) this.markComplete();
      },
    };
  }

  if (kind === "order") {
    return {
      ...base,
      remaining: shuffle(spec.steps_shuffled),
      chosen: [],
      pick(index) {
        if (this.checked && this.correct) return;
        this.chosen.push(this.remaining[index]);
        this.remaining.splice(index, 1);
        this.checked = false;
      },
      undo() {
        if (this.checked && this.correct) return;
        if (!this.chosen.length) return;
        this.remaining.push(this.chosen.pop());
        this.checked = false;
      },
      check() {
        this.checked = true;
        this.correct =
          this.chosen.length === spec.correct_order.length &&
          this.chosen.every((s, i) => s === spec.correct_order[i]);
        if (this.correct) this.markComplete();
      },
    };
  }

  if (kind === "blanks") {
    return {
      ...base,
      answers: {},
      blankKeys: Object.keys(spec.blanks),
      get renderedTemplate() {
        let out = spec.template;
        for (const key of Object.keys(spec.blanks)) {
          const val = this.answers[key] || "______";
          out = out.split("___" + key + "___").join(val);
        }
        return out;
      },
      selectBlank(key, value) {
        if (this.checked && this.correct) return;
        this.answers[key] = value;
        this.checked = false;
      },
      check() {
        this.checked = true;
        this.correct = Object.keys(spec.blanks).every(
          (k) => this.answers[k] === spec.blanks[k].correct
        );
        if (this.correct) this.markComplete();
      },
    };
  }

  if (kind === "scenario") {
    return {
      ...base,
      chosenIndex: null,
      choose(i) {
        this.chosenIndex = i;
        this.checked = true;
        this.correct = !!spec.choices[i].good;
        if (this.correct) this.markComplete();
      },
      tryAgain() {
        this.chosenIndex = null;
        this.checked = false;
      },
    };
  }

  return base;
}
