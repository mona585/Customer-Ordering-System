import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAIScD7fHKBIquvA3MXTKbznpiPeVp9qtI",
  authDomain: "customer-ordering-system-a122c.firebaseapp.com",
  projectId: "customer-ordering-system-a122c",
  storageBucket: "customer-ordering-system-a122c.firebasestorage.app",
  messagingSenderId: "697941381001",
  appId: "1:697941381001:web:a4bab188be638a2f0e1b58",
  measurementId: "G-L62FMM94ES"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app; 