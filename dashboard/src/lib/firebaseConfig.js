// Import the functions you need from the SDKs you need
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getAnalytics, isSupported } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCxnxEFSXOjRHPsxk2jIkZZ1wtUszN9Wnw",
  authDomain: "ai-marketing-system-459423.firebaseapp.com",
  projectId: "ai-marketing-system-459423",
  storageBucket: "ai-marketing-system-459423.firebasestorage.app",
  messagingSenderId: "377241884062",
  appId: "1:377241884062:web:1671a51598a69ed738728f",
  measurementId: "G-H140J3SJEY"
};

// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);
let analytics;

if (typeof window !== "undefined") {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  });
}

export { app, auth, firestore, analytics };

