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
 */
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
        this.correct = this.chosen.join(" ") === spec.correct_command.join(" ");
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
