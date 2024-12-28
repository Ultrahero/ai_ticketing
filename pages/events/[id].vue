<script>
    
import { useCartStore } from "@/stores/cart";
import { computed } from "vue";
import axiosInstance from "~/services/axios";

function getAverageRGB(imgEl) {
    
    var blockSize = 5, // only visit every 5 pixels
        defaultRGB = {r:0,g:0,b:0}, // for non-supporting envs
        canvas = document.createElement('canvas'),
        context = canvas.getContext && canvas.getContext('2d'),
        data, width, height,
        i = -4,
        length,
        rgb = {r:0,g:0,b:0},
        count = 0;
        
    if (!context) {
        return defaultRGB;
    }
    
    height = canvas.height = imgEl.naturalHeight || imgEl.offsetHeight || imgEl.height;
    width = canvas.width = imgEl.naturalWidth || imgEl.offsetWidth || imgEl.width;
    
    context.drawImage(imgEl, 0, 0);
    
    try {
        data = context.getImageData(0, 0, width, height);
    } catch(e) {
        /* security error, img on diff domain */alert('x');
        return defaultRGB;
    }
    
    length = data.data.length;
    
    while ( (i += blockSize * 4) < length ) {
        ++count;
        rgb.r += data.data[i];
        rgb.g += data.data[i+1];
        rgb.b += data.data[i+2];
    }
    
    // ~~ used to floor values
    rgb.r = ~~(rgb.r/count);
    rgb.g = ~~(rgb.g/count);
    rgb.b = ~~(rgb.b/count);
    
    return rgb;
    
}

export default {
    name: "EventPage",
    setup(){
        const cartStore = useCartStore();
        const route = useRoute();
        
        const thisEvent = computed(()=>{
            return cartStore.getEventById(route.params.id)
        });

        const hashtags = computed(()=>{
            return thisEvent.value.hashtags.join(" ");
        });

        // const title_color = computed(()=>{
        //     //get the average image color and lighten to 20%
        //     //use the placeholder image for now
        //     let image1 = document.getElementById('image-1');
        //     let image2 = document.getElementById('image-2');
        //     let image3 = document.getElementById('image-3');
        //     let image4 = document.getElementById('image-4');

        //     let rgb1 = getAverageRGB(image1);
        //     let rgb2 = getAverageRGB(image2);
        //     let rgb3 = getAverageRGB(image3);
        //     let rgb4 = getAverageRGB(image4);

        //     let rgb = {
        //         r: (rgb1.r + rgb2.r + rgb3.r + rgb4.r) / 4,
        //         g: (rgb1.g + rgb2.g + rgb3.g + rgb4.g) / 4,
        //         b: (rgb1.b + rgb2.b + rgb3.b + rgb4.b) / 4
        //     }

        //     //lighten the color
        //     alpha = 1
        //     rgb.r = Math.min(255, 255* (rgb.r/255 / alpha));
        //     rgb.g = Math.min(255, 255* (rgb.g/255 / alpha));
        //     rgb.b = Math.min(255, 255* (rgb.b/255 / alpha));

        //     return `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
        // });
        const title_color = computed(()=>{
            return "rgb(255, 255, 255)";
        });

        return { thisEvent, cartStore, route, hashtags, title_color }
    },
    data() {
        return {
            similar_events: [{
                name: "Loading...",
                id: 1
            }, {
                name: "Loading...",
                id: 2
            }, {
                name: "Loading...",
                id: 3
            }, {
                name: "Loading...",
                id: 4
            }],
            loadingSimilar: false,
            loadingStore: false,

            selectedDate: null,
            selectedSeats: 0,
            menu: false
        }
    },
    methods: {
        async makeSureStoreIsPopulated(){
            if(this.cartStore.events.length === 0){
                this.loadingStore = true;
                this.$emit('loading', this.loadingStore);
                await this.cartStore.fetchEvents();
                this.loadingStore = false;
                this.$emit('loading', this.loadingStore);
            }
        },
        async fetchSimilarEvents(event){
            this.loadingSimilar = true;
            try {
                const response = await axiosInstance.get(`/events/${event.id}/similar`, {
                    params: {
                        count: 4
                    }
                });
                this.similar_events = response.data.similar_events.map((v)=>{return v.event})
            } catch (error) {
                console.error(error);
            }
            this.loadingSimilar = false;
        },
        async addToCart(){
            this.$emit('add-to-cart', {
                id: this.thisEvent.id,
                name: this.thisEvent.name,
                price: Math.min(...this.thisEvent.price),
                dates: this.thisEvent.dates,
                location: this.thisEvent.location,
                short_description: this.thisEvent.short_description
            });
            this.selectedSeats = 0;
            this.selectedDate = null;
            this.menu = false;
        }
    },
    mounted(){
        this.makeSureStoreIsPopulated();
        this.fetchSimilarEvents(this.thisEvent);
    },
    emits: ['add-to-cart', 'loading'],
}
</script>
  
<template>
    <v-container class="event-page py-4">
        
        <v-row >
            <v-col cols="12" md="10" sm="6" class="mx-auto">
            <v-card outlined :style="`background-color:${title_color};`">
                <v-card-title class="text-h5"> {{ thisEvent.name }}</v-card-title>
                <v-card-subtitle class="text-subtitle-2">{{ thisEvent.theme }}</v-card-subtitle>
            
            </v-card>
            </v-col>
        </v-row>
        <!-- Details Section -->

    <v-row class="mt-0" >
        <!-- Gallery Section -->
        <v-col cols="12" md="10" sm="6" class="mx-auto">
          <v-row dense style="background-color: var(--v-theme-background-color);">
            <v-col cols="3" v-for="i in 4" :key="`placeholder-image-${i}`">
              <v-img :src="`/placeholder_${i-1}.jpg`" cover class="rounded-lg" aspect-ratio="0.666" :id="`image-${i}`"/>
            </v-col>
          </v-row>
        </v-col>
    </v-row>
    <v-row class="mb-4 mt-0">
        <v-col cols="12" md="10" sm="6" class="mx-auto">
          <v-card outlined class="details-card" style="width:100%">
            <v-list>
              <v-list-item prepend-icon="mdi-calendar">
                  <v-list-item-title>{{ thisEvent.dates.length>1?'Dates':'Date' }}</v-list-item-title>
                    <p v-for="(date, index) in thisEvent.dates" :key="index" class="v-list-item-subtitle">
                      {{ date }} (Seats Available: {{ thisEvent.seat_count[index] }})
                    </p>
              </v-list-item>
  
              <v-list-item prepend-icon="mdi-map-marker">
                  <v-list-item-title>Location</v-list-item-title>
                  <v-list-item-subtitle>{{ thisEvent.location }}</v-list-item-subtitle>
              </v-list-item>
  
              <v-list-item prepend-icon="mdi-currency-usd">
                  <v-list-item-title>Price</v-list-item-title>
                  <v-list-item-subtitle>from ${{ Math.min(...thisEvent.price) }} per ticket</v-list-item-subtitle>
              </v-list-item>
            </v-list>
  
            <v-card-text>
              <p>{{ hashtags }}</p>
              <br>
              <strong>Description:</strong>
              <p>{{ thisEvent.long_description }}</p>
            </v-card-text>

            <v-row class="mb-2 d-flex justify-center">
            <v-col cols="3" class="d-flex justify-space-around align-center">
                <v-btn icon color="blue">
                    <v-icon>mdi-bookmark</v-icon>
                </v-btn>
                <v-btn icon color="blue">
                    <v-icon>mdi-share-variant</v-icon>
                </v-btn>
            </v-col>
            <v-col cols="3" class="d-flex justify-space-around align-center">
    <v-menu :close-on-content-click="false" v-model="menu">
        <template v-slot:activator="{ props }">
            <v-btn color="success" block v-bind="props">
                Select Your Seats
            </v-btn>
        </template>
        <v-container class="bg-white rounded-lg pa-0">
        <v-form @submit.prevent="addToCart" >
        <v-row>
            <v-col cols="11" class="mx-auto px-2 mt-2">
                <v-select
                    v-model="selectedDate"
                    :items="thisEvent.dates"
                    label="Date"
                    placeholder="Select Date"
                    required
                    class="pb-0"
                ></v-select>
                <v-select
                    v-model="selectedSeats"
                    :items="Array.from({ length: Math.min(thisEvent.seat_count[thisEvent.dates.indexOf(selectedDate)], thisEvent.number_of_tickets_per_buyer || 42) }, (_, i) => i + 1)"
                    label="Seats"
                    placeholder="Select Seats"
                    required
                    class="pb-0"
                ></v-select>
            </v-col>
        </v-row>
        <v-row class="mt-0 pb-2 mx-0">
            <v-col cols="6" class="ma-0 pa-0">
                <v-btn text @click="selectedSeats = 0; selectedDate = null; menu=false" block class="rounded-be-0 rounded-te-0 rounded-ts-0">Dismiss</v-btn>
            </v-col>
            <v-col cols="6" class="ma-0 pa-0">
                <v-btn text color="primary" type="submit" block class="rounded-bs-0 rounded-te-0 rounded-ts-0">Add to Cart</v-btn>
            </v-col>
        </v-row>
    </v-form>
    </v-container>
                    </v-menu>
                </v-col>
            </v-row>
            
            <v-row justify="space-between" class="mt-2"></v-row>
          </v-card>
        </v-col>
    </v-row>
    <v-row>
      <!-- Similar Events Section -->
      <v-col cols="12" md="10" sm="6" class="mx-auto">
      <v-card outlined class="mb-4 bg-teal-lighten-5">
        <v-card-title>Similar Events</v-card-title>
        <v-card-text>
          <v-row dense >
            <v-col cols="4" v-for="i in 3" :key="i">
              <v-card outlined class="bg-white">
                <v-img :src="`/placeholder_${i}.jpg`" aspect-ratio="1" cover>
                </v-img>
                <v-card-title>{{ similar_events[i-1].name }}</v-card-title>
                <v-card-actions>
                    <NuxtLink :to="'/events/' + similar_events[i-1].id">
                        <v-btn text color="primary">View</v-btn>
                    </NuxtLink>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      </v-col>
    </v-row>
        
    </v-container>
</template>

<style scoped>
  .event-page {
    font-family: Arial, sans-serif;
  }
  
  .gallery {
    background-color: #fff3cd;
  }
  
  .details-card {
    background: #fff8e1;
  }
  
  .similar-events {
    background-color: #f9f9f9;
  }
  
  .v-footer {
    padding: 10px;
    background-color: #e0e0e0;
  }
</style>
  