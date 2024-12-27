<template>
    <div class="explore-container" @mouseover="expandExplore" @mouseleave="collapseExplore">
        <div class="explore-bar" :class="{ expanded: isExpanded }">
            <v-icon class="fas fa-explore explore-icon">mdi-compass-outline</v-icon>
            <div v-if="isExpanded" class="explore-input">
                <input type="text" id="exploreInput" placeholder="Explore..."></input>
                <v-icon class="fas fa-filter filter-icon">mdi-filter</v-icon>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            isExpanded: false,
        };
    },
    methods: {
        expandExplore() {
            this.isExpanded = true;
        },
        collapseExplore() {
            this.isExpanded = false;
        },
    },
};
</script>

<style scoped>
.explore-container {
    display: flex;
    align-items: center;
}

.explore-bar {
    display: flex;
    align-items: center;
    transition: width 0.3s ease;
    border: none;
    width: 40px;
    overflow: hidden;
    padding: 5px;
}

.explore-bar.expanded {
    width: 200px;
    border: 1px solid #ccc;
    border-radius: 25px;
}

.explore-input {
    display: flex;
    align-content: space-between;
    flex-direction: row;
    flex-grow: 1;
}

.explore-icon,
.filter-icon {
    margin: 0 2px;
    transition: margin 0.3s ease;
}

.explore-icon.expanded,
.filter-icon.epanded {
    margin: 0 5px;
}

input {
    border: none;
    outline: none;
    width: 100%;
}
</style>