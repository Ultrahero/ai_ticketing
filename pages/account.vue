<template>
    <v-container class="pa-4">
      <v-card>
        <v-tabs v-model="activeTab" align-with-title>
          <v-tab value="one">My Tickets</v-tab>
          <v-tab value="two">User Settings</v-tab>
          <v-tab value="three">AI Integration Settings</v-tab>
        </v-tabs>
  
        <v-tabs-window v-model="activeTab">
          <!-- My Tickets Tab -->
          <v-tabs-window-item value="one">
            <v-container>
              <v-card class="pa-4">
                <v-row>
                  <v-col>
                    <h3 class="text-h6 mb-0">Music & Concerts</h3>
                    <v-list dense v-if="musicTickets.length > 0">
                      <v-list-item v-for="ticket in musicTickets" :key="ticket.id">
                        <v-row class="pa-0 ma-0">
                            <v-col cols="10" class="pa-0 ma-0">
                                <v-list-item-title class="font-weight-bold">{{ ticket.name }}</v-list-item-title>
                            <v-list-item-subtitle> {{ ticket.date }}, {{ ticket.location }}</v-list-item-subtitle>
                          <v-list-item-subtitle> {{ ticket.description }}</v-list-item-subtitle>
                            </v-col>
                            <v-col cols="2" class="pa-0 ma-0 d-flex align-top justify-space-between">
                                
                                <v-btn icon="mdi-share-variant" variant="plain"></v-btn>
                                <v-btn icon="mdi-calendar" variant="plain"></v-btn>
                                <v-btn icon="mdi-close" variant="plain"></v-btn>
                            </v-col>
                        </v-row>
                      </v-list-item>
                    </v-list>
                    <p v-else>No tickets bought</p>
                  </v-col>
                </v-row>
  
                <v-row>
                  <v-col>
                    <h3 class="text-h6 mb-0">Art & Culture</h3>
                    <v-list dense v-if="artTickets.length > 0">
                      <v-list-item v-for="ticket in artTickets" :key="ticket.id">
                        <v-row class="pa-0 ma-0">
                            <v-col cols="10" class="pa-0 ma-0">
                                <v-list-item-title class="font-weight-bold">{{ ticket.name }}</v-list-item-title>
                          <v-list-item-subtitle> {{ ticket.date }}, {{ ticket.location }}</v-list-item-subtitle>
                          <v-list-item-subtitle> {{ ticket.description }}</v-list-item-subtitle>
                            </v-col>
                            <v-col cols="2" class="pa-0 ma-0 d-flex align-top justify-space-between">
                                
                                <v-btn icon="mdi-share-variant" variant="plain"></v-btn>
                                <v-btn icon="mdi-calendar" variant="plain"></v-btn>
                                <v-btn icon="mdi-close" variant="plain"></v-btn>
                            </v-col>
                        </v-row>
                      </v-list-item>
                    </v-list>
                    <p v-else>No tickets bought</p>
                  </v-col>
                </v-row>
              </v-card>
  
              <v-card class="pa-4 mt-4" outlined>
                <h3 class="text-h6">You might like these</h3>
                <v-row dense>
                  <v-col v-for="n in 4" :key="n" cols="3">
                    <v-img
                      src="https://via.placeholder.com/150"
                      aspect-ratio="1"
                      class="elevation-2"
                    ></v-img>
                  </v-col>
                </v-row>
              </v-card>
            </v-container>
          </v-tabs-window-item>
  
          <!-- User Settings Tab -->
          <v-tabs-window-item value="two">
            <v-container>
              <h3>User Settings</h3>
              <v-form>
                <v-text-field label="Username" outlined></v-text-field>
                <v-text-field label="Email" type="email" outlined></v-text-field>
                <v-btn color="primary">Save</v-btn>
              </v-form>
            </v-container>
          </v-tabs-window-item>
  
          <!-- AI Integration Settings Tab -->
          <v-tabs-window-item value="three">
            <v-container>
              <h3>AI Integration Settings</h3>
              <v-form>
                <v-switch label="Enable AI Suggestions"></v-switch>
                <v-select
                  label="Preferred AI Models"
                  :items="['Model A', 'Model B', 'Model C']"
                  outlined
                ></v-select>
                <v-btn color="primary">Save</v-btn>
              </v-form>
            </v-container>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import { useUserStore } from "@/stores/user";
  import axiosInstance from "@/services/axios";
  export default {
    setup(){
        const userStore = useUserStore();
        return {userStore}
    },
    data() {
      return {
        activeTab: 0,
        musicTickets: [],
        artTickets: [],
        allTickets: [],
      };
    },
    mounted(){
        //get all the tickets from the store, then use the backend AI to divide them into music and art tickets
        this.allTickets = this.userStore.tickets;
        this.getTicketTypes(this.allTickets);
    },
    methods: {
        async getTicketTypes(ticketList) {
            if (ticketList.length === 0) return;
            const result = await axiosInstance.post('/get_types', {events: ticketList, types: ["music and concerts", "art and culture"]});
            let ticket_score_types = result.data.events;
            this.musicTickets = ticket_score_types.filter((v)=>{return v.type === "music and concerts"}).map((v)=>{return v.event});
            this.artTickets = ticket_score_types.filter((v)=>{return v.type === "art and culture"}).map((v)=>{return v.event});
            console.log("music tickets", this.musicTickets);
            console.log("art tickets", this.artTickets);
        }
    }
  };
  </script>
  
  <style scoped>
  h3 {
    margin-bottom: 16px;
  }
  </style>
  