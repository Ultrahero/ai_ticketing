<script lang="ts">
import { useUserStore } from '@/stores/user';
import { useCartStore } from '@/stores/cart';

import axiosInstance from '@/services/axios';
import type { loadNuxtConfig } from 'nuxt/kit';

export default {
    async setup() {
        const userStore = useUserStore();
        const cartStore = useCartStore();
        // cartStore.fetchEvents();
        // var tickets = ref(cartStore.events);
        // console.log(tickets);

        return { userStore, cartStore }
    },
    data() {
        return {
            isLoading: false,
            tickets: []
        }
        
    },
    methods: {
        async fetchEvents() 
        {
            this.isLoading = true;
            this.$emit('loading', this.isLoading);
            var response = null;
            if(this.userStore.isAuthenticated()){
                response = await axiosInstance.get('/user/recommendations', {
                headers: {
                    Authorization: `Bearer ${this.userStore.sessionId}`
                },
                params: (this.userStore.location.lat && this.userStore.location.long)? {
                    lat: this.userStore.location.lat,
                    long: this.userStore.location.long,
                }: {}
                });
            }else{
                response = await axiosInstance.get('/recommendations', 
                );
            }
            
            this.tickets = response.data.events;
            this.isLoading = false;
            this.$emit('loading', this.isLoading);
            console.log(this.tickets);
        }
    },
    mounted() {
        this.fetchEvents();
    },
    emits: ['add-to-cart', 'loading'],
}
</script>

<template>
    <v-container>
        <TicketPage :tickets="tickets" @add-to-cart="$emit('add-to-cart', $event)"></TicketPage>
    </v-container>
</template>