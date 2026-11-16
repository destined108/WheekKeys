# Guinea pig sprites

`guinea-pig.png` is an AI-assisted character sheet created using the user's supplied visual reference. It contains four equally spaced columns: awake, walking, chewing, sleeping. It has a transparent background; the renderer crops each cell to its visible silhouette and grounds the feet consistently.

The application reads this file directly. Include `assets` alongside `skins` when packaging. Default colors preserve the original artwork; JSON skin overrides recolor fur regions while retaining shading. Project-provided artwork is distributed under the repository's MIT license.

`guinea-pig-walk.png` is a separate four-frame grounded walk cycle (reach, pass, opposite reach, opposite pass). The renderer uses one scale, a shared 86×62 canvas and a fixed ground line. Gait advances once per six scene pixels traveled, including the mirrored return trip. The body is not rotated or bounced. Travel eases into and out of motion.
