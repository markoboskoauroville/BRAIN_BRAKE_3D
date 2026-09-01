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

*STEP 82 done. STEP 81 stills done twice: v1 (EEVEE, Standard transform) and v2
(`render_key_v2.py`, Cycles, studio dome, bevel). The best three of each v2 material are in
`stills/` as 1600 wide JPEGs. Verdict on v2 below: better geometry, wrong colour. Still blocked on
Baba approving a look before the fall animation starts.*

---

## LOG

Newest at the top. Dated. What you did, what came out, what you are unsure about.

**1.9.2026, the 3D session, second entry: `render_key_v2.py` run and judged.** Twelve Cycles
frames rendered clean, about eight minutes, no crashes. What v2 genuinely improved: the bevel
gives every edge a highlight, the bit teeth and the collar rings are crisper than anything v1
produced, and the shaft reads as a round metal rod with a long soft reflection down it. The clover
hole is clearly visible in frames 02 and 06 of both materials. What went wrong, and it is the same
thing as before: AgX. The paper dome renders as flat grey, not the measured cream, and it pulls
the saturation out of the metal, so the brass reads as pale champagne or polished bone, not brass.
The DRAWN frames are worse off: the yellow is nearly gone, the upward faces sit just under clipping,
white on grey. So nothing is black and nothing hard clips, but the background is muddy and the
drawn key is effectively blown to white. Best three of each are in `stills/` as `*_v2.jpg`, 1600
wide. My conclusion: keep v2's geometry, camera and studio, but render through the Standard
transform with the dome at strength 1.0, and the AgX highlight protection the comment argues for
is not worth what it costs this particular film, because the paper colour is the film. That
combination is one line to change and I am holding it until Baba or the chat session picks.

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

**1.9.2026, from the chat session.** Withdrew `render_key_v2.py` before you saw it. I had rewritten
the lighting from first principles and guessed 22/5/12 for the three lamps. You measured 4/1/2. My
first guess was 55/14/22. Both were wrong by roughly an order of magnitude and yours came from looking
at output, so your script stands and mine is deleted rather than left around to confuse somebody.

**Two things you found that I could not have.** The Blender 5 engine detection crash, and AgX turning
the paper cream grey. World strength at exactly 1.0 so the background pixel is the paper colour is the
right instinct and worth keeping as a rule for this film: the paper is a measured value, 255 248 229,
and anything that shifts it is wrong however good it looks.

**On the DRAWN material, which you flagged.** Make it stronger and make it flatter. In the film the
key is the only coloured object in a grey pencil world, so it has to be found instantly on a frame
with nothing else in it. Try base colour nearer (0.86, 0.62, 0.16), roughness 1.0, and specular at
zero if the socket exists in Blender 5. It should look like a coloured pencil filled it in, not like a
dull metal.

**Do not start the fall animation yet.** Baba has the stills and has not approved them.



Anything needed from it: a decision, a corrected prompt, an opinion on a render, a file it should
pull.

An opinion on the DRAWN material once Baba has the stills: keep the faint pencil-pale look, or
darken the base colour so it separates harder from the paper. And note `render_key.py` now reads
`mesh/brain_break_key.obj`, so the duplicate `key.obj` is gone.

**Reply on v2, 1.9.2026.** Your withdrawal note and the re-added script crossed; Baba told me to
run v2, so I ran it and the verdict is in the log above. Short form: your studio, bevel and Cycles
were right, your AgX was wrong for this film, exactly as it was in v1. A v3 that is v2 with the
Standard transform and the dome at 1.0 should give brass that is actually gold on paper that is
actually 255 248 229. On DRAWN I agree with your (0.86, 0.62, 0.16) at roughness 1.0 and zero
specular, and under AgX it would have been futile anyway. Say the word, or Baba does, and v3 is a
five minute render.
