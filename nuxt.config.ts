// https://nuxt.com/docs/api/configuration/nuxt-config
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import { defineNuxtConfig } from 'nuxt/config'
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  css: [
    'vuetify/styles',
    "@mdi/font/css/materialdesignicons.css",
  ],
  vite: {
    // @ts-ignore
    // curently this will lead to a type error, but hopefully will be fixed soon #justBetaThings
    ssr: {
        noExternal: ['vuetify'], // add the vuetify vite plugin
    },
  },  

  // build: {
  //   transpile: ['vuetify']
  // },

  modules: ['@pinia/nuxt', 
    async (options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', config => config.plugins.push(
          vuetify()
      ))
    }
  ],
})