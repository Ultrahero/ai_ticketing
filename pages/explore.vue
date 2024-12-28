<script lang="ts">
export default {
    async setup() {
        const filter = defineModel('filter', {
            type: Object,
            default: {}
        });
        // cartStore.fetchEvents();
        // var tickets = ref(cartStore.events);
        // console.log(tickets);

        return {filter }
    },
    data() {
        return {
            isLoading: false,
        }
    },
    props: {
        tickets: {
            type: Array,
            default: []
        },
        query: {
            type: String,
            default: ""
        }
    },
    emits: ['add-to-cart'],
    mounted() {
        // Listen for the popstate event when the component is mounted
        window.addEventListener('popstate', this.handleBackButton);

        if (this.query=="")[
            this.$router.push('/')
        ]
    },
    beforeDestroy() {
        // Clean up the event listener when the component is destroyed
        window.removeEventListener('popstate', this.handleBackButton);
    },
    methods: {
        handleBackButton(event) {
        // Check if the current route is the one where you want to intercept the back button
            if (window.location.pathname === '/explore') {
                // Redirect to the index page
                this.$router.push('/');
            }
        }
    }
}
</script>

<template>
    <v-container>
        <TicketPage :tickets="tickets" @add-to-cart="$emit('add-to-cart', $event)"></TicketPage>
    </v-container>
</template>