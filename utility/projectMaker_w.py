import bpy, os
from ..utility import util

def createPackageJson(name, version):
    package_json_content = {
    "name": "nx-runtime-react",
    "private": True,
    "version": "0.0.0",
    "type": "module",
    "scripts": {
      "dev": "vite --host",
      "dev2": "node server.js",
      "dev3": "mkcert create-ca && node server.js",
      "dev4": "gltf-transform optimize public/Scene.glb public/Scene.glb --texture-compress webp && node server.js",
      "build": "tsc && vite build",
      "build-free": "vite build",
      "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
      "preview": "vite preview"
    },
    "dependencies": {
      "@babylonjs/core": "^7.2.1",
      "@babylonjs/inspector": "^7.2.1",
      "@babylonjs/loaders": "^7.2.1",
      "@babylonjs/materials": "^7.2.1",
      "@babylonjs/post-processes": "^7.2.1",
      "ammo.js": "kripken/ammo.js",
      "mkcert": "^3.2.0",
      "express": "^4.18.3",
      "selfsigned": "^2.4.1",
      "ws": "^8.16.0"
    },
    "devDependencies": {
      "typescript": "^5.3.3",
      "vite": "^5.1.4",
      "vite-plugin-mkcert": "^1.17.5"
    }
  }

    return package_json_content


def createExpressServer(assetsPath, port=5173, tcpport=5174):

  convertedPath = assetsPath.replace(os.sep, '/')

  serverConfig = """
// server.js
import express from 'express';
import { createServer } from 'https';
import { readFileSync } from 'fs';
import { createCA, createCert } from "mkcert";

const ca = await createCA({
  organization: "Hello CA",
  countryCode: "NP",
  state: "Bagmati",
  locality: "Kathmandu",
  validity: 365
});

const cert = await createCert({
  ca: { key: ca.key, cert: ca.cert },
  domains: ["127.0.0.1", "localhost"],
  validity: 365
});

const sslOptions = {
  //key: readFileSync('ca.key'),
  //cert: readFileSync('ca.crt')
  key: cert.key,
  cert: cert.cert
};

const app = express();

app.get('/', (req, res) => {
  res.send('Hello, HTTPS world!');
});

createServer(sslOptions, app).listen(5173, () => {
  console.log('HTTPS server running on https://localhost:5173');
});


"""

  return serverConfig