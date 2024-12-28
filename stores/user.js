// stores/user.js
import { defineStore } from "pinia";
import axiosInstance from "~/services/axios";

async function __getUserFromStorage(sessionId){
  try {
    const response = await axiosInstance.get("/getusers/me", {
      headers: { session_id: sessionId },
    });
    user = response.data;
    preferences = user.preferences || [];
  } catch (error) {
    throw error;
  }
  return {sessionId, user, preferences}
};

export const useUserStore = defineStore("user", {

  state: () => ({
    sessionId: null,
    user: null,
    preferences: [],
    location: {
      lat: 0,
      long: 0,
    },
    tickets_: [],
  }),
  getters: {
    session_id: (state) => state.sessionId,
    authenticated: (state) => !!state.sessionId,
    tickets: (state) => state.tickets_,
  },
  actions: {
    async signUp(username, password) {
      try {
        const response = await axiosInstance.post("/signup", { username, password });
        return response.data.message;
      } catch (error) {
        console.log(error)
        throw error
      }
    },
    async login(username, password) {
      const basicAuth = btoa(`${username}:${password}`);
      try {
        console.log("Trying to login with ", username, password);
        const response = await axiosInstance.post("/login", {}, {
          headers: {
            Authorization: `Basic ${basicAuth}`,
          },
        });
        this.sessionId = response.data.session_id;
        //write the sessionId to sessionStorage
        // window_.sessionStorage.setItem("sessionId", this.sessionId);
        await this.getCurrentUser();
        return response.data.message;
      } catch (error) {
        throw error;
      }
    },
    async logout() {
      try {
        if (!this.sessionId) throw "No active session!";
        const response = await axiosInstance.post(
          "/logout",
          {},
          { headers: { session_id: this.sessionId } }
        );
        this.sessionId = null;
        // window_.sessionStorage.removeItem("sessionId"); //remove the sessionId from sessionStorage
        this.preferences = [];
        return response.data.message;
      } catch (error) {
        throw error;
      }
    },
    async getCurrentUser() {
      try {
        if (!this.sessionId) throw "No active session!";
        const response = await axiosInstance.get("/getme", {
          headers: { session_id: this.sessionId },
        });
        this.user = response.data;
        this.preferences = this.user.preferences || [];
      } catch (error) {
        throw error;
      }
    },
    async updatePreferences(additions = [], removals = []) {
      try {
        const response = await axiosInstance.put(
          "/user/preferences",
          { add: additions, remove: removals },
          { headers: { session_id: this.sessionId } }
        );
        this.preferences = response.data.preferences;
        return response.data.message;
      } catch (error) {
        throw error;
      }
    },
    async deleteUser() {
      try {
        if (!this.sessionId) throw "No active session!";
        const response = await axiosInstance.post(
          "/deleteuser",
          {},
          { headers: { session_id: this.sessionId } }
        );
        this.sessionId = null;
        this.user = null;
        this.preferences = [];
        return response.data.message;
      } catch (error) {
        throw error;
      }
    },
    async addTickets(tickets){
      this.tickets_ = this.tickets_.concat(tickets);
    }
  },
});
