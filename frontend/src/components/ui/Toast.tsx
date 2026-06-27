"use client";
import { useEffect } from "react";
import { useUIStore } from "@/store/uiStore";

export default function Toast() {
  const toast = useUIStore((s) => s.toast);
  const clearToast = useUIStore((s) => s.clearToast);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(clearToast, 3500);
    return () => clearTimeout(t);
  }, [toast, clearToast]);

  return (
    <div className={`save-toast${toast ? " show" : ""}`}>
      {toast}
    </div>
  );
}