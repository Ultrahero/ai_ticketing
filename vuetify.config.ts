import { defineVuetifyConfiguration } from 'vuetify-nuxt-module/custom-configuration'

export default defineVuetifyConfiguration({
    icons: {
        defaultSet: 'mdi',
    },
    theme: {
        themes: {
            light: {
                colors: {
                    primary: '#1976D2',
                    secondary: '#424242',
                    tertiary: '#296A9B',
                    accent: '#82B1FF',
                    error: '#FF5252',
                    info: '#2196F3',
                    success: '#4CAF50',
                    warning: '#FB8C00',
                },
            },
            dark: {
                colors: {
                    primary: '#BB86FC',
                    secondary: '#03DAC6',
                    tertiary: '#3AC1A6',
                    accent: '#03DAC6',
                    error: '#CF6679',
                    info: '#2196F3',
                    success: '#4CAF50',
                    warning: '#FB8C00',
                },
            },
        },
    },
})