import {
  fileURLToPath,
} from "node:url";

import {
  dirname,
  resolve,
} from "node:path";

import {
  esmExternalRequirePlugin,
} from "rolldown/plugins";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";


const currentFile =
  fileURLToPath(import.meta.url);

const currentDirectory =
  dirname(currentFile);


export default defineConfig({
  plugins: [
    esmExternalRequirePlugin({
      external: [
        /^react(?:\/.*)?$/,
        /^react-dom(?:\/.*)?$/,
      ],
    }),

    react(),
  ],

  build: {
    lib: {
      entry: resolve(
        currentDirectory,
        "src/index.js",
      ),

      formats: [
        "es",
      ],

      fileName:
        "quantheonix-chatbot",

      cssFileName:
        "chatbot",
    },

    cssCodeSplit: false,
  },
});