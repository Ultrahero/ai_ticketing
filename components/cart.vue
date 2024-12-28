<template>
    <v-container style="width:fit-content;" class="pa-0">
      <!-- Shopping Cart Button -->
      <v-btn
        icon
        @click="toggleCart"
      >
        <v-badge :content="cartItems.length" overlap color="accent">
            <v-icon>mdi-cart</v-icon>
        </v-badge>

      <v-dialog
        v-model="isCartOpen"
        location="right center"
        class="floating-cart"
      >
        <v-card class="mx-2" >
          <v-card-title class="px-4">Shopping Cart</v-card-title>
          <v-card-text class="py-0 px-4">
            <v-list class="pa-0">
              <v-list-item
                v-for="(item, index) in cartItems"
                :key="index" class="rounded-lg cartItem px-2"
                @click="viewEvent(index)"
              >
                <v-row class="pa-0 ma-0">
                  <v-col cols="8" class="pa-0 ma-0 d-inline-flex align-center">
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                  </v-col>
                  <v-col cols="2" class="pa-0 ma-0 d-inline-flex align-center justify-end">
                    <v-list-item-subtitle>{{ item.quantity }} x ${{ item.price }}</v-list-item-subtitle>
                  </v-col>
                  <v-col cols="2" class="pa-0 ma-0 d-inline-flex align-center justify-end">
                    <v-btn @click.stop="removeCartItem(index)" icon="mdi-cart-minus" variant="plain">
                    </v-btn>
                  </v-col>
                </v-row>
              </v-list-item>
              <div v-if="cartItems.length>0">
                <v-list-item style="background-color:rgb(var(--v-theme-primary))" class="rounded-lg px-2">
                <v-row class="pa-0 ma-0">
                  <v-col cols="8" class="pa-0 ma-0 d-inline-flex align-center">
                    <v-list-item-title>Total</v-list-item-title>
                  </v-col>
                  <v-col cols="2" class="pa-0 ma-0 d-inline-flex align-center justify-end">
                    <v-list-item-subtitle >${{ totalPrice }}</v-list-item-subtitle>
                  </v-col>
                  <v-col cols="2"></v-col>
                </v-row>
                </v-list-item>
              </div>
            </v-list>
          </v-card-text>
          <v-card-actions class="py-0 my-0 mx-2">
            <v-btn text @click="closeCart" class="mx-0">Close</v-btn>
            <v-btn style="background-color:rgb(var(--v-theme-accent))" @click="checkout" class="mx-0">Checkout</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      </v-btn>
  
      <!-- Floating Cart Window -->
      
    </v-container>
  </template>
  
  <script>
  export default {
    setup(){
        const cartStore = useCartStore();
        const userStore = useUserStore();
        return {cartStore, userStore}
    },
    data() {
      return {
        isCartOpen: false,
      };
    },
    computed: {
      hasItems() {
        return this.cartStore.count > 0;
      },
      cartItems() {
        return this.cartStore.items;
      },
      totalPrice() {
        return this.cartStore.totalPrice;
      },
    },
    methods: {
      toggleCart() {
        console.log("Toggling cart");
        this.isCartOpen = !this.isCartOpen;
      },
      closeCart() {
        this.isCartOpen = false;
      },
      checkout() {
        //push the events to the user store
        console.log("Checking out");
        this.userStore.addTickets(this.cartStore.items);
        this.cartStore.clearCart();
        this.$emit('checkout');
        this.closeCart();
      },
      viewEvent(index) {
        this.closeCart();
        this.$router.push(`/events/${this.cartItems[index].id}`);
      },
      removeCartItem(index) {
        //get the event from the index
        let e = this.cartItems[index]
        this.cartStore.removeItem(e.name, e.date); //identify the event by name and date
        this.$emit('checkout');//we obuse this event to update the cart in the parent component, it should only affect visuals, thus is fine
      },
    },
    emits: ['checkout'],
  };
  </script>
  
  <style scoped>
  
  .floating-cart {
    width: 400px;
    pointer-events: auto; /* Enables interaction with the card */
  }
  
  .cartItem.hover {
    background-color: rgba(var(--v-theme-secondary), 0.1);
  }
  .cartItem.active {
    background-color: rgba(var(--v-theme-secondary), 0.2);
  }
  </style>
  