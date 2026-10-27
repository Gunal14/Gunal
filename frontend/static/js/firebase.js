import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
    getAnalytics,
    isSupported
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-analytics.js";

const firebaseConfig = {
    apiKey: "AIzaSyCjYzu23q8Vt9VQeSC-oeww0_rmS8B2pZ4",
    authDomain: "smart-monitoring-6755a.firebaseapp.com",
    projectId: "smart-monitoring-6755a",
    storageBucket: "smart-monitoring-6755a.firebasestorage.app",
    messagingSenderId: "636750695368",
    appId: "1:636750695368:web:0c7d6a4ed912c74cc58efd",
    measurementId: "G-F9MGSVWGD0"
};

const app = initializeApp(firebaseConfig);

isSupported()
    .then((supported) => {
        if (supported) {
            window.firebaseAnalytics = getAnalytics(app);
        } else {
            console.info("Firebase Analytics is not supported in this browser.");
        }
    })
    .catch((error) => {
        console.error("Failed to initialize Firebase Analytics.", error);
    });
