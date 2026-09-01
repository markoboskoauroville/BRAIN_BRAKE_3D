# EXCHANGE_3D.md

**The 3D session writes here. The chat session reads.**

Steps come the other way, from `MANTRA_MANIFEST/EXCHANGE.md`. Nothing is written to that file from
this session: two sessions on one file produce a merge conflict in the thing everybody depends on.

**Push after every meaningful step, not at the end.** Nobody can see your terminal. If it is not
committed it does not exist.

**Say what you are unsure about.** A render you think is wrong but cannot say why is worth writing
down, and so is any guess you had to make because a step did not cover something.

---

## STATUS

Rewritten each time. What is done, what is running, what is blocked and on what.

*STEP 82 done: repository created, four folders, .gitignore in the first commit. STEP 81 stills
done: twelve renders in `renders/` on the Mac, checked by eye, brass reads as brass. Blocked on
Baba seeing the stills before the fall animation starts, as the step requires.*

---

## LOG

Newest at the top. Dated. What you did, what came out, what you are unsure about.

**1.9.2026, the 3D session.** Twelve stills rendered headless with Blender 5.2.1 LTS, EEVEE.
Three fixes to `render_key.py`, all pushed: the engine detection crashed on Blender 5 (a Hydra
subclass has no `bl_idname`), so engines are now tried in order. The default AgX view transform
rendered the paper cream as grey and washed the brass to near white, so the view transform is
Standard and the world strength is exactly 1.0, which makes the background pixel the paper colour
itself. The three guessed lamp energies came down from 55/14/22 to 4/1/2 across two rounds of
looking at the output. Unsure about: the DRAWN material. At (0.93, 0.76, 0.30) diffuse it reads
as a soft butter yellow against the cream, visible but faint. If it should read stronger, the fix
is a darker or more saturated base colour, not the lamps.

---

## FOR THE CHAT SESSION

Anything needed from it: a decision, a corrected prompt, an opinion on a render, a file it should
pull.

An opinion on the DRAWN material once Baba has the stills: keep the faint pencil-pale look, or
darken the base colour so it separates harder from the paper. And note `render_key.py` now reads
`mesh/brain_break_key.obj`, so the duplicate `key.obj` is gone.
