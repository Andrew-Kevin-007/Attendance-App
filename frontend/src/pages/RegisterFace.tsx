import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUser } from "@/lib/api";
import { attendanceAPI } from "@/lib/attendance";
import { Loader2, Camera, CheckCircle2, AlertCircle, ArrowLeft, UserPlus, RefreshCw } from "lucide-react";
import Navigation from "@/components/Navigation";

const RegisterFace: React.FC = () => {
  const navigate = useNavigate();
  const current = getUser();
  const [users, setUsers] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<number | "">("");
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string>("");
  const [addSample, setAddSample] = useState(false); // New: toggle for adding training sample
  const [status, setStatus] = useState<
    | { state: "idle" }
    | { state: "capturing" }
    | { state: "processing" }
    | { state: "success"; msg: string }
    | { state: "error"; msg: string }
  >({ state: "idle" });

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const isAllowed = current?.role === "admin" || current?.role === "manager";

  const initCamera = async () => {
    setCameraError("");
    setCameraReady(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setCameraReady(true);
      }
    } catch (err: any) {
      setCameraError(err?.message || "Unable to access camera. Please allow permission.");
    }
  };

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await attendanceAPI.listUsers();
        setUsers(data);
        
        // Auto-select current user if they're not admin/manager (self-registration)
        if (!isAllowed && current?.id) {
          setSelectedId(current.id);
        }
      } catch (e: any) {
        // Silently fail - users list is optional
      } finally {
        setLoadingUsers(false);
      }
    };

    fetchUsers();
    initCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        (videoRef.current.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      }
    };
  }, [isAllowed, current, navigate]);

  const captureAndRegister = async () => {
    if (!videoRef.current || !canvasRef.current || !selectedId) return;
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
      const res = await attendanceAPI.registerFace(Number(selectedId), dataUrl, addSample);
      setStatus({ state: "success", msg: res.message || "Face registered successfully!" });
    } catch (e: any) {
      let msg = "Registration failed";
      if (e?.message) {
        msg = typeof e.message === "string" ? e.message : JSON.stringify(e.message);
      }
      setStatus({ state: "error", msg });
    }
  };

  const selectedUser = users.find((u) => u.id === selectedId);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate("/dashboard")}
            className="p-2 rounded-xl hover:bg-muted/50 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-3">
              <UserPlus className="h-6 w-6 text-primary" />
              Register Employee Face
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Enroll a team member's face for attendance tracking
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Panel - Employee Selection */}
          <div className="lg:col-span-1 space-y-6">
            <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
              <h2 className="text-sm font-medium mb-4">
                {isAllowed ? "Select Employee" : "Register Your Face"}
              </h2>
              
              {isAllowed ? (
                <>
                  <select
                    className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    value={selectedId}
                    onChange={(e) => {
                      setSelectedId(e.target.value ? Number(e.target.value) : "");
                      setStatus({ state: "idle" });
                    }}
                    disabled={loadingUsers}
                  >
                    <option value="">{loadingUsers ? "Loading employees..." : "Choose an employee"}</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name} ({u.email})
                      </option>
                    ))}
                  </select>

                  {selectedUser && (
                    <div className="mt-4 p-4 rounded-xl bg-muted/30 border border-border/40">
                      <p className="text-sm font-medium">{selectedUser.name}</p>
                      <p className="text-xs text-muted-foreground">{selectedUser.email}</p>
                      <span className="inline-block mt-2 px-2 py-0.5 rounded-full text-xs bg-primary/10 text-primary capitalize">
                        {selectedUser.role}
                      </span>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-4 rounded-xl bg-primary/10 border border-primary/20">
                  <p className="text-sm font-medium">{current?.name}</p>
                  <p className="text-xs text-muted-foreground mt-1">{current?.email}</p>
                  <p className="text-xs text-primary mt-2 font-medium">
                    ✓ You're registering your own face
                  </p>
                </div>
              )}

              {/* Training Mode Toggle */}
              {selectedId && (
                <div className="mt-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                  <label className="flex items-start gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={addSample}
                      onChange={(e) => setAddSample(e.target.checked)}
                      className="mt-0.5 w-4 h-4 rounded border-border text-primary focus:ring-2 focus:ring-primary/20"
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium group-hover:text-primary transition-colors">
                        Add Training Sample
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Add an additional photo to improve recognition accuracy
                      </p>
                    </div>
                  </label>
                </div>
              )}
            </div>

            {/* Instructions */}
            <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
              <h2 className="text-sm font-medium mb-3">Instructions</h2>
              <ul className="space-y-2 text-xs text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-medium">1</span>
                  Select an employee from the dropdown
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-medium">2</span>
                  Position face clearly within the circle
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-medium">3</span>
                  Ensure good lighting (avoid backlighting)
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-medium">4</span>
                  Click "Capture & Register" to save
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/30 text-blue-600 flex items-center justify-center text-[10px] font-medium">💡</span>
                  <strong>Tip:</strong> Add 2-3 training samples from different angles for best accuracy
                </li>
              </ul>
            </div>
          </div>

          {/* Right Panel - Camera */}
          <div className="lg:col-span-2">
            <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl overflow-hidden">
              {/* Camera Feed */}
              <div className="relative aspect-video bg-black">
                <video 
                  ref={videoRef} 
                  className="h-full w-full object-cover" 
                  playsInline 
                  muted 
                />
                
                {/* Overlay */}
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/30" />
                  
                  {/* Face guide circle */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className={`h-56 w-56 md:h-72 md:w-72 rounded-full border-[3px] transition-colors duration-300 ${
                      status.state === "success" ? "border-emerald-400" : 
                      status.state === "error" ? "border-red-400" : 
                      "border-white/40"
                    } shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]`} />
                  </div>
                </div>

                {/* Camera Error */}
                {cameraError && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-white">
                    <AlertCircle className="h-12 w-12 text-amber-400 mb-4" />
                    <p className="text-sm mb-4">{cameraError}</p>
                    <button
                      onClick={initCamera}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 text-sm transition-colors"
                    >
                      <RefreshCw className="h-4 w-4" /> Retry
                    </button>
                  </div>
                )}

                {/* Status Badges */}
                {status.state === "processing" && (
                  <div className="absolute top-4 left-4 inline-flex items-center gap-2 rounded-full bg-white/20 backdrop-blur-md px-4 py-2 text-sm text-white">
                    <Loader2 className="h-4 w-4 animate-spin" /> Processing face...
                  </div>
                )}
                {status.state === "success" && (
                  <div className="absolute top-4 left-4 inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 text-sm text-white shadow-lg">
                    <CheckCircle2 className="h-4 w-4" /> {status.msg}
                  </div>
                )}
                {status.state === "error" && (
                  <div className="absolute top-4 left-4 inline-flex items-center gap-2 rounded-full bg-red-500 px-4 py-2 text-sm text-white shadow-lg max-w-[80%]">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" /> 
                    <span className="truncate">{status.msg}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="p-6 flex items-center justify-between border-t border-border/40">
                <p className="text-xs text-muted-foreground">
                  {cameraReady ? "Camera ready" : "Initializing camera..."}
                </p>
                
                <button
                  onClick={captureAndRegister}
                  disabled={!selectedId || !cameraReady || status.state === "processing"}
                  className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-6 py-2.5 text-sm font-medium shadow-lg hover:shadow-xl hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-lg transition-all"
                >
                  {status.state === "processing" ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Processing...
                    </>
                  ) : (
                    <>
                      <Camera className="h-4 w-4" /> 
                      {addSample ? "Add Training Sample" : "Capture & Register"}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default RegisterFace;
