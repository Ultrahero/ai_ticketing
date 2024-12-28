<template>
    <v-card>
      <v-card-title>Welcome, {{ userStore.user?.username || "Guest" }} !</v-card-title>

        <v-container v-if="userStore.session_id" class="ma-0 pa-0">
            <v-card-text class="py-0">
                You are logged in!
            </v-card-text>
            <v-card-actions class="d-flex flex-column align-center">
                <button @click="handleLogout" v-if="userStore.session_id" block>Logout</button>
            </v-card-actions>
        </v-container>
        <v-container v-else class="ma-0 pa-0">
            <v-card-text class="py-0">
                <p>Sign in to access your account</p>
                <v-text-field v-model="_username" placeholder="Your Name" label="Username" density="compact"/>
                <v-text-field v-model="_password" :type="pwd_type?`password`:`text`" placeholder="Secure Password" label="Password" density="compact" append-inner-icon="mdi-eye" @click:append-inner="pwd_type!=pwd_type"/>
            </v-card-text>
            <v-card-actions class="d-flex flex-column align-center">
                <v-btn id="loginButton" @click="handleLogin" color="primary" block tonal>Login</v-btn>
                <v-btn id="changeToSignup" @click="loadSignup" block outlined>Create New Instead</v-btn>
            </v-card-actions>
        </v-container>
    </v-card>
</template>
  
<script>
import { useUserStore } from "@/stores/user";
import { ref } from "vue";

export default {
    setup(){
        const userStore = useUserStore();
        return {userStore}
    },
    mounted(){
        //create a hook that listens to [ENTER] keypresses and triggers the login function
        window.addEventListener('keypress', (e) => {
            if(e.key === 'Enter'){
                this.handleLogin();
            }
        });
    },
    unmounted(){
        window.removeEventListener('keypress', (e) => {
            if(e.key === 'Enter'){
                this.handleLogin();
            }
        });
    },
    data() {
        return {
            _username: "",
            _password: "",
            error: null,
            message: null,
            pwd_type: false
        };
    },
    methods:{
        async handleLogin() {
            try {
                await this.userStore.login(this._username, this._password);
                alert("Logged in!");
                this.$emit('loginSubmitted', {username: this._username, password: this._password});
            } catch (error) {
                alert(error);
            }
            

        },
        async handleLogout(){
            try {
                await this.userStore.logout();
                alert("Logged out!");
                this.$emit('loggedOut');
            } catch (error) {
                alert(error);
            }
            
        },
        loadSignup(){
            this.$emit('changeToSignup', {username: this._username, password: this._password}); //we conveniently pass the username and password to the parent component, so that if the user decides to sign up, they don't have to retype the username and password
        }
    },
    emits: ['changeToSignup', 'loginSubmitted', 'loggedOut'],
    props: {
        username: {
            type: String,
            required: false
        },
        password: {
            type: String,
            required: false
        }
    },
    onload(){
        this._username = this.username;
        this._password = this.password;
    }
};
</script>