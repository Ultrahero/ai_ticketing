<script lang="ts">
import { useCartStore } from '@/stores/cart';
import { useTheme } from 'vuetify'
import axiosInstance from './services/axios';
import { set } from 'ol/transform';
export default {
  setup() {
    const theme = useTheme()
    function toggleTheme () {
      theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
    }

    const cartStore = useCartStore();

    cartStore.fetchEvents();

    return { cartStore, toggleTheme }
  },
  data() {
    return {
      drawer: true,
      drawer_permanent:true,
      drawer_hover: false,
      editingOrder: false,

      rail_width: '60',

      filter: {
        location: [38.89853520573355, -77.03586539092846], //longitude, latitude [default is Washington DC]
        radius: 1000,//in km
        price: Infinity, //less than or equal, in dollars
        date: new Date(), //date
        daytime: -1, //0: morning, 1: afternoon, 2: evening, 3: night, -1: any
      },
      signup_instead: false,
      showLogin: false,
      tmp_username: "",
      tmp_password: "",

      cart_not_empty: false,

      isLoading: false,
    }
  },
  methods: {
    pages() {
      return ([
        { title: 'Recommendations', icon: 'mdi-flask-outline', to: '/', pageID: 'index' },
        { title: 'Account', icon: 'mdi-account-circle', to: '/account', pageID: 'account' },
        // { title: 'Explore', icon: 'mdi-compass-outline', to: '/explore', pageID: 'explore' },
        { title: 'Near You', icon: 'mdi-map-marker', to: '/near_you', pageID: 'near_you' },
        { title: 'Hot Stuff', icon: 'mdi-fire', to: '/hot_stuff', pageID: 'hot_stuff' },
        // { title: 'Search', icon: 'mdi-magnify', to: '/search', pageID: 'search' },
        // { title: 'Ticket', icon: 'mdi-ticket', to: '/ticket', pageID: 'ticket' },
        { title: 'About', icon: 'mdi-information', to: '/about', pageID: 'about' },
        
        { title: 'Unknown Page', icon: 'mdi-help', to: '/unknown', pageID: 'unknown' }
      ].concat(this.cartStore.availableEvents.map((event) => { return {
       title: "Event - " + event.name, icon: 'mdi-ticket', to: '/events/' + event.id, pageID: 'events-id'
      }}))
    )},
    getPageName() {
      const page_name = this.$route.name || 'unknown';
      console.log('Page Name:', page_name);
      let page = this.pages().find(page => page.pageID == page_name)
      if (page) {
        return page.title
      }else{
        return 'Unknown Page'
      } 
    },
    leaveHoverDrawer(){
      this.drawer_hover = false;
      //set the drawer to false when the mouse leaves the drawer, if the drawer is not permanent
      if(!this.drawer_permanent){
        this.drawer = false;
      }
      //set the editingOrder to false when the mouse leaves the drawer
      if (this.editingOrder) {
        this.editOrder();
      }
    },
    editOrder() {
      console.log('Edit Order');
      this.editingOrder = !this.editingOrder;

      if (this.editingOrder) {
        this.$nextTick(() => {
          const listItems = this.$el.querySelectorAll('.v-navigation-drawer .v-list-item');

          // Create a single placeholder element
          const placeholder = document.createElement('div');
          placeholder.className = 'placeholder';
          placeholder.style.height = listItems[0].offsetHeight + 'px';
          placeholder.style.border = '2px dashed rgba(0, 0, 0, 0.3)';
          placeholder.style.margin = '5px 0';

          let draggedIndex: number = null;

          listItems.forEach((item:HTMLBodyElement, index:number) => {
            item.setAttribute('draggable', 'true');

            // Store the index of the dragged item
            item.ondragstart = (event:DragEvent) => {
              draggedIndex = index;
              event.dataTransfer!.effectAllowed = 'move';
              event.dataTransfer!.setData('text/plain', index.toString());
              item.style.opacity = '0.2'; // Add a semi-transparent effect
            };

            item.ondragover = (event:DragEvent) => {
              event.preventDefault(); // Allow drop
              if (!placeholder.parentNode || placeholder.parentNode !== item.parentNode) {
                // Ensure placeholder is in the correct parent
                item.parentNode?.insertBefore(placeholder, item);
              } else if (placeholder.nextSibling !== item) {
                // Reposition placeholder if necessary
                item.parentNode.insertBefore(placeholder, item);
              }
            };

            item.ondrop = (event:MouseEvent) => {
              event.preventDefault();
              const targetIndex = Array.from(item.parentNode!.children).indexOf(placeholder);

              if (draggedIndex !== null) {
                
                // Remove the dragged item from its original position
                const draggedItem = this.pages().splice(draggedIndex, 1)[0];

                // Insert the dragged item at the placeholder's position
                this.pages().splice(targetIndex - (targetIndex>draggedIndex?1:0), 1, draggedItem);
                
                
                console.error("Updated pages: ", this.pages());
                // Reset variables
                draggedIndex = null;
              }

              // Remove the placeholder
              if (placeholder.parentNode) {
                placeholder.parentNode.removeChild(placeholder);
              }

              // Reset styles
              item.style.opacity = '';
            };

            item.ondragend = () => {
              // Ensure everything is reset on drag end
              if (placeholder.parentNode) {
                placeholder.parentNode.removeChild(placeholder);
              }
              item.style.opacity = '';
            };
          });
        });
      } else {
        const listItems = this.$el.querySelectorAll('.v-navigation-drawer .v-list-item .page-list-items');
        listItems.forEach((item:HTMLBodyElement) => {
          item.removeAttribute('draggable');
          item.ondragstart = null;
          item.ondragover = null;
          item.ondrop = null;
          item.ondragend = null;
        });
      }

    },
    checkHoverDrawer(event:MouseEvent){
      //if the mouse is n the left side, activate the drawer
      if (event.clientX < 1){
        this.drawer = true;
      }
    },
    toggleDrawerPermanancy() {
      this.drawer_permanent = !this.drawer_permanent;
      this.drawer = this.drawer_permanent;
    },
    changeLoginToSignup(event: { username: string; password: string; }) {
      this.tmp_username = event.username;
      this.tmp_password = event.password;
      this.signup_instead = true;
    },
    changeSignupToLogin(event: { username: string; password: string; }) {
      this.tmp_username = event.username;
      this.tmp_password = event.password;
      this.signup_instead = false;
    },
    resetLoginMenu(){
      this.showLogin=false; 
      this.tmp_username=""; 
      this.tmp_password=""
    },
    async searchEvents() {
      const response = await axiosInstance.post("http://localhost:8000/search", {
        preferences: this.preferences, //one string, comma separated
        keywords: this.keywords, //one string, comma separated
        location: [this.selected_location.lat, this.selected_location.lng],
      });
      this.results = response.data.ranked_events; //array of event objects with rank: [{event: event, rank: rank}]
    },
    cartChange(){//gets called when the cart changes
      this.card_not_empty = this.cartStore.count() > 0;
    },
    addToCart(event){
      this.cartStore.addEvent(event);
      this.cartChange();
    },
    setProgressBar(isLoading:boolean){
      this.isLoading = isLoading;
    }
  },
}
</script>

<template>
  <v-app>
    <v-app-bar density="compact" color="background">
      <template v-slot:prepend>
        <nuxt-link class="app-bar-link" to="/">
          <v-img src="/logo_letter_dense.png" class="ml-2" max-height="40" style="width: 32px;"></v-img>
        </nuxt-link>
      </template>

      <v-app-bar-title>
        <nuxt-link class="app-bar-link" to="/">{{ getPageName() }}</nuxt-link>
      </v-app-bar-title>
      <!-- <v-spacer></v-spacer> -->
      <div class="center-actions">
        <search></search>
        <explore></explore>
      </div>
      <!-- <v-spacer></v-spacer> -->
      <nuxt-link class="app-bar-link" to="/">
        <v-btn icon dense>
          <v-icon>mdi-flask-outline</v-icon>
        </v-btn>
      </nuxt-link>
      <nuxt-link class="app-bar-link" to="/hot_stuff">
        <v-btn icon dense>
          <v-icon>mdi-fire</v-icon>
        </v-btn>
      </nuxt-link>
      <nuxt-link class="app-bar-link" to="/near_you">
        <v-btn icon dense>
          <v-icon>mdi-map-marker</v-icon>
        </v-btn>
      </nuxt-link>
      <nuxt-link class="app-bar-link" to="/account">
        <v-btn icon dense id="account-avatar-icon">
          <v-icon>mdi-account</v-icon>
              
          <v-menu location="bottom end" class="ma-0 pa-0" id="login-menu" activator="parent" open-on-hover :close-on-content-click="false" v-model="showLogin">
            <Login v-if="!signup_instead" :username="tmp_username" :password="tmp_password" @changeToSignup="changeLoginToSignup" @loginSubmitted="resetLoginMenu" class="ma-0 pa-0"></Login>
            <Signup v-else :username="tmp_username" :password="tmp_password" @changeToLogin="changeSignupToLogin"  @signupSubmitted="resetLoginMenu" class="ma-0 pa-0"></Signup>
          </v-menu>
        </v-btn>
      </nuxt-link>

      <Cart v-if="cart_not_empty"></Cart>

      <template v-slot:append>
        <v-app-bar-nav-icon @click.stop="rail_width=rail_width==`220`?`60`:`220`"></v-app-bar-nav-icon>
      </template>
    </v-app-bar>
    <v-progress-linear v-if="isLoading" color="secondary" indeterminate></v-progress-linear>

    <v-main @mousemove="checkHoverDrawer">


      <v-navigation-drawer permanent rail :rail-width="rail_width" v-model="drawer" app @mouseover="drawer_hover = true" @mouseleave="leaveHoverDrawer()">
        <v-list nav class="d-flex flex-column" style="height: calc(100% - 50px);">
          <v-list-item class="page-list-items" v-for="page in pages().filter((p) => p.pageID != 'unknown' && !p.pageID.startsWith('events'))" :prepend-icon="page.pageID == 'index' ? 'mdi-home' : page.icon" :to="page.to" :key="page.pageID">
            <v-list-item-title>{{ page.title }}</v-list-item-title>
          </v-list-item>

          <v-spacer id="navbar-spacer"></v-spacer>

          <v-list-item v-if="drawer_hover" @click="editOrder" :prepend-icon="editingOrder ? 'mdi-pencil-off' : 'mdi-pencil'">
            <v-list-item-title>{{ editingOrder ? 'Stop Editing':'Edit Order' }} </v-list-item-title>
          </v-list-item>

          <v-list-item v-if="drawer_hover" @click="toggleDrawerPermanancy()" :prepend-icon="drawer_permanent ? 'mdi-close':'mdi-pause'">
            <v-list-item-title>{{ drawer ? 'Close' : 'Show'}}</v-list-item-title>
          </v-list-item>

          <v-list-item v-if="drawer_hover" @click="toggleTheme" prepend-icon="mdi-theme-light-dark">
            <v-list-item-title>Toggle Theme</v-list-item-title>
          </v-list-item>

        </v-list>
      </v-navigation-drawer>

      <v-container>
          <NuxtPage @loading="setProgressBar"/>
      </v-container>

    </v-main>

    <v-footer color="purple-lighten-2" class="sticky-footer">
      <div class="footer-div">
        <span>&copy; 2024 AI Ticketing - 2024952850 - COSE43200 </span>
        <nuxt-link to="/about" class="app-bar-link">About Us</nuxt-link>
      </div>
    </v-footer>  
  </v-app>
</template>


<style>

.sticky-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  z-index:1005; 
  height: fit-content; 
  max-height: 50px;
}

.v-toolbar-title .v-app-bar-title, .v-toolbar-title__placeholder {
  width: fit-content;
}

.v-toolbar__content{
  display: flex;
  justify-content: center;
  position: relative;
  height: fit-content;
}

.center-actions {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: row;
  align-items: center;
}

.footer-div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-bar-link {
  color: rgb(var(--v-theme-text-color));
  text-decoration: none;
}

.placeholder {
  border: 2px dashed rgba(0, 0, 0, 0.3);
  background-color: rgba(0, 0, 0, 0.05);
  margin: 5px 0;
}

.v-overlay__content {
  margin : 0;
  padding : 0;
}
</style>