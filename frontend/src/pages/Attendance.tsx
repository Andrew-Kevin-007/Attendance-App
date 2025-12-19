import React, { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { attendanceAPI, formatElapsedTime, AttendanceStatus } from "@/lib/attendance";
import { getUser } from "@/lib/api";
import Navigation from "@/components/Navigation";
import {
  CheckCircle2,
  Loader2,
  AlertCircle,
  UserX,
  Clock,
  LogIn,
  LogOut,
  Timer,
  ArrowLeft,
  Camera,
} from "lucide-react";

const Attendance: React.FC = () => {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [streamError, setStreamError] = useState<string>("");
  const [attendanceStatus, setAttendanceStatus] = useState<AttendanceStatus | null>(null);
  const [checkingStatus, setCheckingStatus] = useState(true);
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);
  const [cameraActive, setCameraActive] = useState(false);
  const [checkoutMode, setCheckoutMode] = useState(false);
  const [status, setStatus] = useState<
    | { state: "idle" }
    | { state: "capturing" }
    | { state: "processing" }
    | { state: "success"; name: string; message: string }
    | { state: "error"; message: string }
  >({ state: "idle" });

  const user = getUser();

  // Stop camera stream
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, []);

  // Start camera stream
  const startCamera = useCallback(async () => {
    try {
      setStreamError("");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
    } catch (err: any) {
      setStreamError(err?.message || "Unable to access the camera. Please allow permissions.");
    }
  }, []);

  // Fetch attendance status
  const fetchStatus = useCallback(async () => {
    try {
      const res = await attendanceAPI.statusToday();
      setAttendanceStatus(res);
      
      if (res.checkedIn && res.elapsedSeconds != null) {
        setElapsedSeconds(res.elapsedSeconds);
      }
    } catch {
      setAttendanceStatus({ registered: false, markedToday: false, checkedIn: false, checkedOut: false });
    } finally {
      setCheckingStatus(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Auto-start camera only if not checked in yet
  useEffect(() => {
    if (attendanceStatus?.registered && !attendanceStatus?.checkedIn) {
      startCamera();
    }
    
    return () => {
      stopCamera();
    };
  }, [attendanceStatus?.registered, attendanceStatus?.checkedIn, startCamera, stopCamera]);

  // Real-time elapsed timer when checked in but not out
  useEffect(() => {
    if (!attendanceStatus?.checkedIn || attendanceStatus?.checkedOut) return;
    
    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [attendanceStatus?.checkedIn, attendanceStatus?.checkedOut]);

  // Handle starting checkout mode
  const handleStartCheckout = async () => {
    setCheckoutMode(true);
    await startCamera();
  };

  // Handle canceling checkout
  const handleCancelCheckout = () => {
    setCheckoutMode(false);
    stopCamera();
    setStatus({ state: "idle" });
  };

  const captureAndSubmit = async (action: "check_in" | "check_out") => {
    if (!videoRef.current || !canvasRef.current) return;
    setStatus({ state: "capturing" });

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const w = video.videoWidth || 640;
    const h = video.videoHeight || 480;
    canvas.width = w;
    canvas.height = h;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, w, h);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);

    setStatus({ state: "processing" });
    try {
      const res = action === "check_in"
        ? await attendanceAPI.checkIn(dataUrl)
        : await attendanceAPI.checkOut(dataUrl);
      
      const name = res.employee_name || "";
      setStatus({ state: "success", name, message: res.message });
      
      // Update local state
      if (res.elapsedSeconds != null) {
        setElapsedSeconds(res.elapsedSeconds);
      }
      
      // Stop camera after successful action
      stopCamera();
      setCheckoutMode(false);
      
      // Refresh status after a brief delay
      setTimeout(() => {
        fetchStatus();
        setStatus({ state: "idle" });
      }, 1500);
    } catch (e: any) {
      setStatus({ state: "error", message: e.message || "Failed to mark attendance" });
    }
  };

  // Loading state
  if (checkingStatus) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Checking attendance status...</p>
        </div>
      </div>
    );
  }

  // Not registered state
  if (attendanceStatus?.registered === false) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] p-6">
          <div className="w-full max-w-md">
            <div className="rounded-3xl border border-border/60 bg-card/70 backdrop-blur-xl shadow-xl overflow-hidden">
              <div className="p-8 md:p-10 text-center">
                <div className="mx-auto mb-6 h-16 w-16 rounded-full bg-amber-500/10 flex items-center justify-center">
                  <UserX className="h-8 w-8 text-amber-500" />
                </div>
                <h1 className="text-2xl font-semibold tracking-tight mb-2">Face Not Registered</h1>
                <p className="text-sm text-muted-foreground mb-6">
                  Your face hasn't been registered in the system yet. Please contact your administrator
                  or manager to register your face before you can mark attendance.
                </p>
                <button
                  onClick={() => navigate("/dashboard")}
                  className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-5 py-2 text-sm font-medium shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary/30"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Completed state - both check-in and check-out done
  if (attendanceStatus?.checkedIn && attendanceStatus?.checkedOut) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] p-6">
          <div className="w-full max-w-lg">
            <div className="rounded-3xl border border-border/60 bg-card/70 backdrop-blur-xl shadow-xl overflow-hidden">
              <div className="p-8 md:p-10 text-center">
                <div className="mx-auto mb-6 h-20 w-20 rounded-full bg-emerald-500/10 flex items-center justify-center">
                  <CheckCircle2 className="h-10 w-10 text-emerald-500" />
                </div>
                <h1 className="text-2xl font-semibold tracking-tight mb-2">Attendance Complete!</h1>
                <p className="text-sm text-muted-foreground mb-6">
                  You've completed your attendance for today.
                </p>
                
                {/* Time Summary Card */}
                <div className="bg-muted/50 rounded-2xl p-6 mb-6">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-emerald-600 mb-1">
                        <LogIn className="h-4 w-4" />
                        <span className="text-xs font-medium">Check In</span>
                      </div>
                      <p className="text-lg font-semibold">
                        {attendanceStatus.checkInTime
                          ? new Date(attendanceStatus.checkInTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                          : "--:--"}
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-blue-600 mb-1">
                        <Timer className="h-4 w-4" />
                        <span className="text-xs font-medium">Duration</span>
                      </div>
                      <p className="text-lg font-semibold font-mono">
                        {formatElapsedTime(attendanceStatus.elapsedSeconds)}
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-orange-600 mb-1">
                        <LogOut className="h-4 w-4" />
                        <span className="text-xs font-medium">Check Out</span>
                      </div>
                      <p className="text-lg font-semibold">
                        {attendanceStatus.checkOutTime
                          ? new Date(attendanceStatus.checkOutTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                          : "--:--"}
                      </p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => navigate("/dashboard")}
                  className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-6 py-2.5 text-sm font-medium shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary/30"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Checked in state - show summary with checkout option
  if (attendanceStatus?.checkedIn && !checkoutMode) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="container-apple py-8">
          <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="mb-6">
              <button
                onClick={() => navigate("/dashboard")}
                className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </button>
              <h1 className="text-3xl font-semibold tracking-tight">Attendance</h1>
              <p className="text-muted-foreground mt-1">
                You're checked in. Have a productive day!
              </p>
            </div>

            {/* Status Card */}
            <div className="rounded-3xl border border-border/60 bg-card/70 backdrop-blur-xl shadow-xl overflow-hidden mb-6">
              <div className="p-8">
                {/* Success Badge */}
                <div className="flex items-center justify-center mb-6">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 text-emerald-600 px-4 py-2">
                    <CheckCircle2 className="h-5 w-5" />
                    <span className="font-medium">Checked In</span>
                  </div>
                </div>

                {/* Time Display */}
                <div className="text-center mb-8">
                  <p className="text-sm text-muted-foreground mb-2">Time Elapsed</p>
                  <p className="text-5xl font-mono font-bold tracking-tight text-foreground">
                    {formatElapsedTime(elapsedSeconds)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Since {attendanceStatus?.checkInTime
                      ? new Date(attendanceStatus.checkInTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                      : "--:--"}
                  </p>
                </div>

                {/* Check-in Details */}
                <div className="flex items-center justify-center gap-8 py-4 border-t border-border">
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 text-emerald-600 mb-1">
                      <LogIn className="h-4 w-4" />
                      <span className="text-xs font-medium">Check In</span>
                    </div>
                    <p className="text-lg font-semibold">
                      {attendanceStatus?.checkInTime
                        ? new Date(attendanceStatus.checkInTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                        : "--:--:--"}
                    </p>
                  </div>
                  <div className="h-12 w-px bg-border" />
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                      <LogOut className="h-4 w-4" />
                      <span className="text-xs font-medium">Check Out</span>
                    </div>
                    <p className="text-lg font-semibold text-muted-foreground">
                      Pending
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Checkout Button */}
            <div className="rounded-3xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Ready to leave?</h3>
                  <p className="text-sm text-muted-foreground">
                    Check out to complete your attendance for today
                  </p>
                </div>
                <button
                  onClick={handleStartCheckout}
                  className="inline-flex items-center gap-2 rounded-full bg-orange-600 text-white px-6 py-2.5 text-sm font-medium shadow hover:bg-orange-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-orange-500/30 transition-all"
                >
                  <Camera className="h-4 w-4" />
                  Start Check Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Camera view for check-in or check-out
  const isCheckingIn = !attendanceStatus?.checkedIn;
  const actionLabel = isCheckingIn ? "Check In" : "Check Out";
  const actionColor = isCheckingIn ? "emerald" : "orange";

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="container-apple py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <button
              onClick={() => {
                if (checkoutMode) {
                  handleCancelCheckout();
                } else {
                  navigate("/dashboard");
                }
              }}
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              {checkoutMode ? "Cancel Check Out" : "Back to Dashboard"}
            </button>
            <h1 className="text-3xl font-semibold tracking-tight">{actionLabel}</h1>
            <p className="text-muted-foreground mt-1">
              {user?.name ? `${user.name}, ` : ""}
              {isCheckingIn
                ? "Start your workday by checking in with face recognition."
                : "Complete your workday by checking out with face recognition."}
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Camera Section */}
            <div className="lg:col-span-2">
              <div className="rounded-3xl border border-border/60 bg-card/70 backdrop-blur-xl shadow-xl overflow-hidden">
                <div className="p-6">
                  <div className="relative aspect-video rounded-2xl overflow-hidden bg-black/70 border border-border">
                    <video ref={videoRef} className="h-full w-full object-cover opacity-95" playsInline muted />

                    {/* Loading camera overlay */}
                    {!cameraActive && !streamError && (
                      <div className="absolute inset-0 flex items-center justify-center bg-black/80">
                        <div className="text-center">
                          <Loader2 className="h-8 w-8 animate-spin text-white mx-auto mb-2" />
                          <p className="text-sm text-white/70">Starting camera...</p>
                        </div>
                      </div>
                    )}

                    {/* Glass overlay and guide ring */}
                    {cameraActive && (
                      <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/20" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className={`h-48 w-48 md:h-56 md:w-56 rounded-full border-2 shadow-[0_0_0_9999px_rgba(0,0,0,0.25)] ${
                            actionColor === "emerald" ? "border-emerald-400/50" : "border-orange-400/50"
                          }`} />
                        </div>
                      </div>
                    )}

                    {/* Status badge */}
                    {status.state === "processing" && (
                      <div className="absolute top-3 left-3 inline-flex items-center gap-2 rounded-full bg-white/10 backdrop-blur px-3 py-1 text-xs text-white">
                        <Loader2 className="h-3.5 w-3.5 animate-spin" /> Processing...
                      </div>
                    )}
                    {status.state === "success" && (
                      <div className="absolute top-3 left-3 inline-flex items-center gap-2 rounded-full bg-emerald-500/90 backdrop-blur px-3 py-1 text-xs text-white">
                        <CheckCircle2 className="h-3.5 w-3.5" /> {status.message}
                      </div>
                    )}
                    {status.state === "error" && (
                      <div className="absolute top-3 left-3 inline-flex items-center gap-2 rounded-full bg-destructive/90 backdrop-blur px-3 py-1 text-xs text-white">
                        <AlertCircle className="h-3.5 w-3.5" /> {status.message}
                      </div>
                    )}
                  </div>

                  {streamError && (
                    <div className="mt-4 text-sm text-destructive flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 mt-0.5" />
                      <span>{streamError}</span>
                    </div>
                  )}

                  <div className="mt-6 flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      Secure face recognition. No images stored.
                    </div>
                    <button
                      onClick={() => captureAndSubmit(isCheckingIn ? "check_in" : "check_out")}
                      disabled={status.state === "processing" || !cameraActive}
                      className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-medium shadow hover:shadow-md focus:outline-none focus:ring-2 disabled:opacity-60 transition-all ${
                        actionColor === "emerald"
                          ? "bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500/30"
                          : "bg-orange-600 text-white hover:bg-orange-700 focus:ring-orange-500/30"
                      }`}
                    >
                      {status.state === "processing" ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" /> Processing...
                        </>
                      ) : isCheckingIn ? (
                        <>
                          <LogIn className="h-4 w-4" /> Check In
                        </>
                      ) : (
                        <>
                          <LogOut className="h-4 w-4" /> Check Out
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Status Sidebar */}
            <div className="space-y-4">
              {/* Current Status */}
              <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-5">
                <h3 className="font-medium text-sm text-muted-foreground mb-4">Today's Status</h3>
                
                <div className="space-y-4">
                  {/* Check In Status */}
                  <div className={`flex items-center gap-3 p-3 rounded-xl ${
                    attendanceStatus?.checkedIn ? "bg-emerald-500/10" : "bg-muted/30"
                  }`}>
                    <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      attendanceStatus?.checkedIn ? "bg-emerald-500 text-white" : "bg-muted text-muted-foreground"
                    }`}>
                      <LogIn className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">Check In</p>
                      <p className="text-xs text-muted-foreground">
                        {attendanceStatus?.checkInTime
                          ? new Date(attendanceStatus.checkInTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                          : "Pending"}
                      </p>
                    </div>
                    {attendanceStatus?.checkedIn && (
                      <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
                    )}
                  </div>

                  {/* Check Out Status */}
                  <div className={`flex items-center gap-3 p-3 rounded-xl ${
                    attendanceStatus?.checkedOut ? "bg-orange-500/10" : "bg-muted/30"
                  }`}>
                    <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      attendanceStatus?.checkedOut ? "bg-orange-500 text-white" : "bg-muted text-muted-foreground"
                    }`}>
                      <LogOut className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">Check Out</p>
                      <p className="text-xs text-muted-foreground">
                        {attendanceStatus?.checkOutTime
                          ? new Date(attendanceStatus.checkOutTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                          : "Pending"}
                      </p>
                    </div>
                    {attendanceStatus?.checkedOut && (
                      <CheckCircle2 className="h-5 w-5 text-orange-500 flex-shrink-0" />
                    )}
                  </div>
                </div>
              </div>

              {/* Elapsed Time (only show during checkout) */}
              {checkoutMode && attendanceStatus?.checkedIn && (
                <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Clock className="h-4 w-4 text-blue-500" />
                    <h3 className="font-medium text-sm text-muted-foreground">Time Elapsed</h3>
                  </div>
                  <div className="text-center py-4">
                    <p className="text-4xl font-mono font-bold tracking-tight text-foreground">
                      {formatElapsedTime(elapsedSeconds)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">Since check-in</p>
                  </div>
                </div>
              )}

              {/* Instructions */}
              <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-5">
                <h3 className="font-medium text-sm text-muted-foreground mb-3">Instructions</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-primary">1.</span>
                    Position your face in the circle
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary">2.</span>
                    Ensure good lighting
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary">3.</span>
                    Click the {actionLabel} button
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Offscreen canvas */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default Attendance;
