import React from "react";
import { useAuth } from "@/lib/authContext"; // Adjust path as needed
import { useRouter } from "next/navigation"; // Corrected import for App Router

const SignInPage = () => {
  const { user, signInWithGoogle, signOut, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return <p>Loading...</p>;
  }

  const handleSignIn = async () => {
    try {
      await signInWithGoogle();
      // Router push can be conditional based on where you want to redirect
      // For now, let's assume successful sign-in keeps them on a page that shows user info
    } catch (error) {
      console.error("Sign in failed", error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push("/signin"); // Redirect to sign-in page after sign out
    } catch (error) {
      console.error("Sign out failed", error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Authentication</h1>
      {user ? (
        <div>
          <p>Welcome, {user.displayName || user.email}!</p>
          <p>User ID: {user.uid}</p>
          <button onClick={handleSignOut} style={{ padding: "10px", marginTop: "10px" }}>
            Sign Out
          </button>
        </div>
      ) : (
        <div>
          <p>You are not signed in.</p>
          <button onClick={handleSignIn} style={{ padding: "10px", marginTop: "10px" }}>
            Sign In with Google
          </button>
        </div>
      )}
    </div>
  );
};

export default SignInPage;

