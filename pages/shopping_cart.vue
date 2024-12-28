<template>
  <v-container>
    <v-sheet>
      <!-- Music & Concerts Section -->
      <v-row>
        <v-col cols="12">
          <v-card outlined>
            <v-card-title class="font-weight-bold">Music & Concerts</v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-item v-for="(item, index) in musicConcerts" :key="index">
                  <v-list-item-content>
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ item.description }} - {{ item.time }} - {{ item.location }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    ${{ item.price }}
                    <v-btn icon @click="removeItem(index, 'musicConcerts')">
                      <v-icon>mdi-cart-remove</v-icon>
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Art & Culture Section -->
      <v-row>
        <v-col cols="12">
          <v-card outlined>
            <v-card-title class="font-weight-bold">Art & Culture</v-card-title>
            <v-card-text>None Selected</v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-divider></v-divider>
      <!-- Total Price and Actions -->
      <v-row class="my-2">
        <v-col cols="12" class="text-right">
          <h4>Total: ${{ total }}</h4>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col cols="12" class="text-right">
            <v-btn color="primary" class="mt-2" @click="checkout">
            Buy above Tickets
          </v-btn>
        </v-col>
      </v-row>

    </v-sheet>
    <div class="spacer"></div>
    <v-sheet>
      <!-- Artist Goodies -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card outlined>
            <v-card-title class="font-weight-bold">Goodies of your favourite Artists 7 Exhibitions</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="3" v-for="(goodie, index) in goodies" :key="index">
                  <v-img :src="goodie.image" contain aspect-ratio="1"></v-img>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-sheet>
  </v-container>
</template>
  
  <script>
  export default {
    data() {
      return {
        musicConcerts: [
          {
            name: "Concert A",
            description: "Short Description",
            time: "7:00 PM",
            location: "Location A",
            price: 50,
          },
          {
            name: "Concert B",
            description: "Short Description",
            time: "9:00 PM",
            location: "Location B",
            price: 16,
          },
        ],
        goodies: [
            { image: "placeholder_0.jpg" },
            { image: "placeholder_1.jpg" },
            { image: "placeholder_2.jpg" },
            { image: "placeholder_3.jpg" },
            // { image: "placeholder_4.jpg" },
            ],
      };
    },
    computed: {
      total() {
        return this.musicConcerts.reduce((sum, item) => sum + item.price, 0);
      },
    },
    methods: {
      removeItem(index, list) {
        this[list].splice(index, 1);
      },
      checkout() {
        alert("Proceeding to checkout...");
      },
    },
  };
  </script>
  