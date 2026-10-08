"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { RoleGuard } from "@/components/RoleGuard";
import { api } from "@/lib/api";
import { User, Role } from "@/lib/types";
import { Users, UserPlus, Shield, Check, X } from "lucide-react";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<Role>("employee");
  const [msg, setMsg] = useState<string | null>(null);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await api.admin.listUsers();
      setUsers(res);
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim() || !newName.trim()) return;
    try {
      await api.admin.createUser({
        name: newName,
        email: newEmail,
        role: newRole,
        organization_id: "org-twinos-demo-001",
      });
      setMsg(`User ${newEmail} created successfully.`);
      setNewName("");
      setNewEmail("");
      loadUsers();
      setTimeout(() => setMsg(null), 3000);
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="space-y-6">
        {/* Admin Nav Subheader */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
          <Link href="/admin/users" className="px-3 py-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 text-xs font-bold border border-indigo-500/30">
            User Management
          </Link>
          <Link href="/admin/connections" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            Platform Connections
          </Link>
          <Link href="/admin/risk-config" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            Risk Configuration
          </Link>
          <Link href="/admin/audit" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            Audit Logs
          </Link>
        </div>

        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Users className="w-6 h-6 text-indigo-400" />
            User and Role Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Provision users, assign RBAC access levels, and audit permission roles
          </p>
        </div>

        {msg && (
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs">
            {msg}
          </div>
        )}

        {/* Create User Form */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 shadow-xl">
          <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-3 flex items-center gap-2">
            <UserPlus className="w-4 h-4 text-emerald-400" />
            Provision New User
          </h3>

          <form onSubmit={handleCreateUser} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <input
              type="text"
              placeholder="Full Name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              required
            />
            <input
              type="email"
              placeholder="Email address"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              required
            />
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value as Role)}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition"
            >
              Add User
            </button>
          </form>
        </div>

        {/* Users Table */}
        <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface/80 border-b border-slate-800 text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Name</th>
                <th className="p-4">Email</th>
                <th className="p-4">RBAC Role</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30 transition">
                  <td className="p-4 font-bold text-white">{u.name}</td>
                  <td className="p-4 font-mono text-slate-400">{u.email}</td>
                  <td className="p-4">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {u.role}
                    </span>
                  </td>
                  <td className="p-4 text-emerald-400 font-semibold flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    Active
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </RoleGuard>
  );
}
