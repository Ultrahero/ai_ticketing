import { createVuetify } from 'vuetify'
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

export default defineNuxtPlugin((nuxtApp) => {
    const vuetify = createVuetify({
        components,
        directives,
        ssr: true,
        icons: {
            defaultSet: 'mdi',
        },
        theme: {
            defaultTheme: 'light',
            themes: {
                light: {
                    colors: {
                        text: '#040316',
                        background: '#fbfbfe',
                        primary: '#FFCD29',
                        secondary: '#E4CCFF',
                        accent: '#f79c1d',
                        error: '#FF5252',
                        info: '#2196F3',
                        success: '#4CAF50',
                        warning: '#FB8C00',
                    },
                },
                dark: {
                    colors: {
                        text: '#eae9fc',
                        background: '#010104',
                        primary: '#d6a400',
                        secondary: '#180033',
                        accent: '#e28708',
                        error: '#CF6679',
                        info: '#2196F3',
                        success: '#4CAF50',
                        warning: '#FB8C00',
                    },
                },
            },
        },
    })
    nuxtApp.vueApp.use(vuetify);
})