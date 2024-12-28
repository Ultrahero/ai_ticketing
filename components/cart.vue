<template>
    <v-container>
      <!-- Shopping Cart Button -->
      <v-btn
        icon
        @click="toggleCart"
      >
        <v-badge :content="cartItems.length" overlap>
            <v-icon>mdi-cart</v-icon>
        </v-badge>
      </v-btn>
  
      <!-- Floating Cart Window -->
      <v-overlay
        v-if="cartItems.length > 0"
        :value="isCartOpen"
        class="floating-cart-overlay"
      >
        <v-card class="floating-cart">
          <v-card-title>Shopping Cart</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(item, index) in cartItems"
                :key="index"
              >
                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.quantity }} x {{ item.price }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="checkout">Checkout</v-btn>
            <v-btn text @click="closeCart">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-overlay>
    </v-container>
  </template>
  
  <script>
  export default {
    setup(){
        const cartStore = useCartStore();
        return {cartStore}
    },
    data() {
      return {
        isCartOpen: false,
      };
    },
    computed: {
      hasItems() {
        return this.cartItems.length > 0;
      },
      cartItems() {
        return this.cartStore.cartItems;
      },
    },
    methods: {
      toggleCart() {
        this.isCartOpen = !this.isCartOpen;
      },
      closeCart() {
        this.isCartOpen = false;
      },
      checkout() {
        alert("Proceeding to checkout!");
        this.closeCart();
      },
    },
  };
  </script>
  
  <style scoped>
  .floating-cart-overlay {
    position: fixed;
    top: 80;
    right: 10;
    bottom: auto;
    left: auto;
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    pointer-events: none; /* Makes the overlay ignore clicks */
  }
  
  .floating-cart {
    width: 300px;
    margin: 16px;
    pointer-events: auto; /* Enables interaction with the card */
  }
  </style>
  