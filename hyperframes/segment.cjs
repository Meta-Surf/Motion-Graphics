// Local CPU inference; all paths supplied by the Python adapter, no network.
const fs = require('node:fs');
const ort = require('onnxruntime-node');
(async () => {
  const session = await ort.InferenceSession.create(process.argv[2], {executionProviders: ['cpu']});
  const bytes = fs.readFileSync(process.argv[3]);
  const data = new Float32Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 4);
  const result = await session.run({[session.inputNames[0]]: new ort.Tensor('float32', data, [1, 3, 320, 320])});
  const mask = result[session.outputNames[0]];
  fs.writeFileSync(process.argv[4], Buffer.from(mask.data.buffer, mask.data.byteOffset, mask.data.byteLength));
})().catch(error => {console.error(error.message); process.exit(1);});
