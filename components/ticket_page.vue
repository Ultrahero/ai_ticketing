<template>
    <div>
        <section class="page-header">
            <slot name="upper-page"></slot>
        </section>
        <section class="ticket-grid">
            <ticket-card v-for="ticket in tickets" :key="ticket.id" :ticket="ticket" @add-to-cart="(event)=>{$emit('add-to-cart', event)}"/>
        </section>
    </div>
</template>

<script>
export default {
    name: 'TicketPage',
    props: {
        tickets: {
            type: Array,
            required: true
        }
    },
    emits: ['add-to-cart']
}
</script>

<style scoped>
.ticket-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
}

.ticket {
    border: 1px solid #ccc;
    padding: 16px;
    border-radius: 8px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}
</style>