import React, { useState, useEffect } from "react";
import axios from "axios";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { useWallet } from "@solana/wallet-adapter-react";
import { DevnetWalletContext } from "./components/WalletConnectButton";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "@solana/wallet-adapter-react-ui/styles.css";
import "./App.css";

function Dashboard() {
  const [form, setForm] = useState({
    volatility: 0.5,
    collateral_ratio: 1.2,
    leverage: 2,
    asset_price: 2000,
    market_trend: 0.1,
  });

  const [result, setResult] = useState(null);
  const [walletRisk, setWalletRisk] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [walletLoading, setWalletLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const { publicKey } = useWallet();
  const walletAddress = publicKey ? publicKey.toBase58() : "";

  // update wallet info on connect
  useEffect(() => {
    if (walletAddress) {
      setWalletRisk({ wallet: walletAddress, category: "Connected" });
    }
  }, [walletAddress]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: parseFloat(e.target.value) });
  };

  // 🔮 Predict Risk
  const handleSubmit = async () => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/predict-risk", form, {
        headers: { "Content-Type": "application/json" },
      });

      const data = res.data;
      setResult(data);
      setHistory((prev) => [
        ...prev,
        {
          run: prev.length + 1,
          probability: data.risk_probability,
          class: data.risk_class,
        },
      ]);
    } catch (err) {
      console.error(err);
      setErrorMsg("❌ Could not connect to backend. Ensure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  // 🧠 Auto-fill from wallet API
  const handleCheckWallet = async () => {
    if (!walletAddress) {
      setErrorMsg("⚠️ Please connect your wallet first.");
      return;
    }

    setWalletLoading(true);
    setErrorMsg(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/wallet-risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet_address: walletAddress }),
      });

      const data = await res.json();

      setForm({
        volatility: data.volatility,
        collateral_ratio: data.collateral_ratio,
        leverage: data.leverage,
        asset_price: data.asset_price,
        market_trend: data.market_trend,
      });

      setWalletRisk({
        wallet: walletAddress,
        score: data.risk_score || null,
        category: data.risk_category || "N/A",
      });
    } catch (err) {
      console.error(err);
      setErrorMsg("⚠️ Failed to fetch wallet parameters. Check backend API.");
    } finally {
      setWalletLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden p-6">
      {/* 3D Ambient Effects */}
      <div className="background-3d" />
      <div className="orb" />
      <div className="orb" />

      <div className="glass-card fade-in w-full max-w-3xl relative z-10">
        {/* Header */}
        <h1 className="gradient-text text-3xl text-center mb-6">
          ALLXDefi Risk Dashboard (using ASI)
        </h1>

        {/* Wallet Connect */}
        <div className="flex justify-center mb-4">
          <WalletMultiButton className="wallet-btn" />
        </div>

        {/* Wallet Auto-Fill */}
        <div className="glass-card p-4 mb-6">
          <h2 className="text-lg font-semibold text-center gradient-text mb-3">
            Wallet Risk Auto-Fill
          </h2>
          <div className="flex justify-center">
            <button
              onClick={handleCheckWallet}
              disabled={walletLoading}
              className="btn-primary neon-hover"
            >
              {walletLoading ? "Fetching..." : "Auto-Fill From Wallet"}
            </button>
          </div>
          {walletRisk && (
            <div className="mt-4 text-sm text-center text-gray-300">
              <p><strong>Wallet:</strong> {walletRisk.wallet}</p>
              <p><strong>Category:</strong> {walletRisk.category}</p>
            </div>
          )}
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-2 gap-4">
          {Object.keys(form).map((key) => (
            <div key={key}>
              <label className="block text-sm font-medium text-gray-300 capitalize mb-1">
                {key.replace("_", " ")}
              </label>
              <input
                type="number"
                step="0.01"
                name={key}
                value={form[key]}
                onChange={handleChange}
              />
            </div>
          ))}
        </div>

        {/* Run Risk Button */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary neon-hover w-full mt-6"
        >
          {loading ? "Analyzing..." : "Run Risk Analysis"}
        </button>

        {/* Error Message */}
        {errorMsg && (
          <div className="mt-4 text-sm text-red-400 bg-red-500/10 p-2 rounded border border-red-500/30 text-center">
            {errorMsg}
          </div>
        )}

        {/* Risk Report */}
        {result && (
          <div className="glass-card p-4 mt-6 text-center">
            <h2 className="text-xl font-semibold gradient-text mb-2">
              Risk Report
            </h2>
            <p>
              Probability:{" "}
              <span className="font-bold text-cyan-400">
                {result.risk_probability?.toFixed(2)}%
              </span>
            </p>
            <p>
              Class:{" "}
              <span className="font-bold text-fuchsia-400">
                {result.risk_class}
              </span>
            </p>
            <p className="italic text-gray-400 mt-2">{result.message}</p>
          </div>
        )}

        {/* Chart */}
        {history.length > 0 && (
          <div className="chart-box mt-8">
            <h3 className="text-lg font-semibold text-center gradient-text mb-3">
              Risk Probability Trend
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={history}>
                <Line
                  type="monotone"
                  dataKey="probability"
                  stroke="#a855f7"
                  strokeWidth={3}
                  dot={{ r: 5 }}
                />
                <CartesianGrid stroke="#4c1d95" strokeDasharray="4 4" />
                <XAxis dataKey="run" tick={{ fill: "#c084fc" }} />
                <YAxis tick={{ fill: "#c084fc" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1e0033",
                    border: "1px solid #9333ea",
                    color: "white",
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <DevnetWalletContext>
      <Dashboard />
    </DevnetWalletContext>
  );
}
