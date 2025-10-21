"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { API_URL } from "@/utils/auth_fn";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Chrome } from "lucide-react";
import Link from "next/link";
export function LoginForm({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("manufacturer");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch(`${API_URL}/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      console.log("🔄 Fetch response status:", response.status);

      const data = await response.json();
      console.log("🟢 API Response:", data);

      if (!response.ok) {
        console.error("❌ Login failed:", data);
        setError(data.detail || "Invalid username or password");
        return;
      }

      if (data.access) {
        console.log("✅ Login Successful!");
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        // Fetch user's company
      const companyRes = await fetch(`${API_URL}/company/`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${data.access}`,
        },
      });
      if (companyRes.ok) {
        const companies = await companyRes.json();
        // If only one company, store its id
        if (Array.isArray(companies) && companies.length > 0) {
          localStorage.setItem("company_id", companies[0].id);
        }
      }
        if (role === "manufacturer") {
          router.replace("/manufacturer");
        } else if (role === "employee") {
          router.replace("/employee");
        } else if (role === "retailer") {
          router.replace("/retailer");
        }
      } else {
        console.error("❌ Unexpected response format:", data);
        setError("Unexpected error. Please try again.");
      }
    } catch (err) {
      console.error("🚨 Fetch Error:", err);
      setError("Server error. Please check if the backend is running.");
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="bg-black text-white border border-white-300 w-full md:w-96">
        <CardHeader className="pb-2">
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription className="text-gray-400 border-b border-gray-600 pb-2">
            Enter your username below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4">
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  required
                  className="bg-gray-900 text-white border border-gray-700"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm text-blue-400 underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  className="bg-gray-900 text-white border-gray-700"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="role">Select Role</Label>
                <select
                  id="role"
                  className="bg-gray-900 text-white border border-gray-700"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="manufacturer">Manufacturer</option>
                  <option value="employee">Employee</option>
                  <option value="retailer">Retailer</option>
                </select>
              </div>
              {error && <p className="text-red-500 text-sm">{error}</p>}
              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                Login
              </Button>
              <Button
                variant="outline"
                className="w-full text-gray-300 border-gray-600 hover:bg-gray-800 hover:text-white"
              >
                Login with Google
                <Chrome className="ml-2 h-4 w-4" />
              </Button>
            </div>
            <div className="mt-4 text-center text-sm">
              Don&apos;t have an account?{" "}
              <Link
                href="/authentication/signup"
                className="text-blue-400 underline underline-offset-4"
              >
                Sign up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
