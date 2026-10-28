# Native template library

`src/hyperframes_bridge.py` compiles existing `photo_essay` and `layers` scenes to
editable HTML subcompositions, with contained foreground layers and a separate
caption host. Layout comes from `hyperframes/profiles/artificial-curiosity.json`.

These are native HyperFrames interpretations of the shared content contract, not
pixel-identical conversions of Remotion. Unsupported `object3d`, `dataflow`,
`cutaway`, `scale`, `compare`, and video scenes are rejected explicitly; continue
rendering those with Remotion or author and validate a dedicated HyperFrames scene.

More native components are available with the pinned CLI:

```
npm --prefix hyperframes run hf -- catalog --query "camera" --json
npm --prefix hyperframes run hf -- catalog --query "caption" --json
```

Install selected registry source into a private working project, not every catalog
item into Git. Local output, model binaries and user media stay outside source.
