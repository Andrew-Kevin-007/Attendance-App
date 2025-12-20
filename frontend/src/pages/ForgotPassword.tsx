import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Mail } from "lucide-react";
import { passwordAPI } from "@/lib/api";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await passwordAPI.forgotPassword(email);
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || "Failed to send reset email. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="h-12 flex items-center justify-center border-b border-divider">
          <span className="font-semibold">Smart Task AI</span>
        </header>

        <main className="flex-1 flex items-center justify-center px-6">
          <div className="w-full max-w-sm text-center">
            <div className="mb-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="headline-large mb-3">Check your email</h1>
              <p className="subhead">
                If an account with <strong>{email}</strong> exists, we've sent a password reset link.
              </p>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="link-apple text-sm"
              >
                Try again with a different email
              </button>
            </div>

            <div className="mt-8">
              <Link to="/" className="link-apple text-sm flex items-center justify-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to login
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="h-12 flex items-center justify-center border-b border-divider">
        <span className="font-semibold">Smart Task AI</span>
      </header>

      <main className="flex-1 flex items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <div className="text-center mb-10 opacity-0 animate-fade-in-up">
            <h1 className="headline-large mb-3">Reset Password</h1>
            <p className="subhead">Enter your email to receive a password reset link.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 opacity-0 animate-fade-in-up delay-200">
            {error && (
              <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            <div>
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-apple w-full"
                required
              />
            </div>

            <button
              type="submit"
              className="btn-apple-primary w-full mt-6"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>

          <div className="text-center mt-8 opacity-0 animate-fade-in delay-400">
            <Link to="/" className="link-apple text-sm flex items-center justify-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to login
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ForgotPassword;
