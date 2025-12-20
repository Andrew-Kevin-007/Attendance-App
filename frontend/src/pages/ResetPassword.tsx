import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, XCircle } from "lucide-react";
import { passwordAPI } from "@/lib/api";

const ResetPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setError("Invalid or missing reset token. Please request a new password reset.");
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      await passwordAPI.resetPassword(token!, password);
      setSuccess(true);
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate("/");
      }, 3000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password. The link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="h-12 flex items-center justify-center border-b border-divider">
          <span className="font-semibold">Smart Task AI</span>
        </header>

        <main className="flex-1 flex items-center justify-center px-6">
          <div className="w-full max-w-sm text-center">
            <div className="mb-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="headline-large mb-3">Password Reset!</h1>
              <p className="subhead">
                Your password has been successfully reset. You can now log in with your new password.
              </p>
            </div>

            <p className="text-sm text-muted-foreground mb-4">
              Redirecting to login...
            </p>

            <Link to="/" className="link-apple text-sm">
              Go to login now
            </Link>
          </div>
        </main>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="h-12 flex items-center justify-center border-b border-divider">
          <span className="font-semibold">Smart Task AI</span>
        </header>

        <main className="flex-1 flex items-center justify-center px-6">
          <div className="w-full max-w-sm text-center">
            <div className="mb-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="headline-large mb-3">Invalid Link</h1>
              <p className="subhead">
                This password reset link is invalid or has expired.
              </p>
            </div>

            <Link to="/forgot-password" className="btn-apple-primary inline-block">
              Request New Reset Link
            </Link>

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
            <h1 className="headline-large mb-3">Set New Password</h1>
            <p className="subhead">Enter your new password below.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 opacity-0 animate-fade-in-up delay-200">
            {error && (
              <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            <div>
              <input
                type="password"
                placeholder="New password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-apple w-full"
                required
                minLength={6}
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-apple w-full"
                required
                minLength={6}
              />
            </div>

            <button
              type="submit"
              className="btn-apple-primary w-full mt-6"
              disabled={loading}
            >
              {loading ? "Resetting..." : "Reset Password"}
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

export default ResetPassword;
