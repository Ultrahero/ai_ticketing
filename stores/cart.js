import { defineStore } from "pinia";
import axiosInstance from "~/services/axios";

export const useCartStore = defineStore("cart", {
  state: () => ({
    cart: [], // Array to hold cart entries
    availableEvents: [], // Array to hold available events
  }),
  getters: {
    // Get total price of the cart
    totalPrice: (state) => {
      return state.cart.reduce((sum, item) => {
        return sum + item.price * item.quantity;
      }, 0);
    },
    // Get total quantity of items in the cart
    totalQuantity: (state) => {
      return state.cart.reduce((sum, item) => sum + item.quantity, 0);
    },
    events : (state) => {
        return state.availableEvents;
    }
  },
  actions: {
    // Add an event to the cart
    addEvent(event, dateIndex, quantity) {
      const date = event.dates[dateIndex];
      const price = event.price[dateIndex];

      // Check if the event on this date is already in the cart
      const existingItem = this.cart.find(
        (item) => item.name === event.name && item.date === date
      );

      if (existingItem) {
        // Update the quantity of the existing item
        existingItem.quantity += quantity;
      } else {
        // Add a new entry to the cart
        this.cart.push({
          name: event.name,
          date,
          location: event.location,
          price,
          quantity,
        });
      }
    },
    // Remove an event from the cart
    removeEvent(eventName, date) {
        this.cart = this.cart.filter(
        (item) => !(item.name === eventName && item.date === date)
      );
    },
    // Update the quantity of an event in the cart
    updateQuantity(eventName, date, quantity) {
      const item = this.cart.find(
        (item) => item.name === eventName && item.date === date
      );

      if (item) {
        item.quantity = quantity;

        // Remove the item if quantity is set to 0
        if (item.quantity <= 0) {
          this.removeEvent(eventName, date);
        }
      }
    },
    // Clear the cart
    clearCart() {
        this.cart = [];
    },
    count(){
        return this.cart.length;
    },
    async fetchEvents(){
        return axiosInstance.get("/events").then((response) => {
            this.availableEvents = []; // Set the available events
            response.data.events.forEach((event) => {
              // Add the event to the available events array
              this.availableEvents.push(event);
            });

            // Sort the available events by name
            // console.log(this.availableEvents);
            this.availableEvents.sort((a, b) => {
              return a.name.localeCompare(b.name);
            });

            // Sort the dates of each event
            this.availableEvents.forEach((event) => {
              event.dates.sort();
            });


        });
    },
    getEventById(id){
        return this.availableEvents.find((event) => event.id === parseInt(id));
    }
  },
});
