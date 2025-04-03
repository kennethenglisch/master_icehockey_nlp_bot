"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import {
  ChevronLeft,
  Settings,
  Send,
  Bot,
  User,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Eye,
  EyeOff,
  HelpCircle,
  Loader2,
} from "lucide-react"

const GPT_MODELS = [
  { value: "gpt-4o-mini", label: "GPT-4o Mini" },
  { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-3", label: "GPT-3" },
]

const EMBEDDER_MODELS = [{ value: "sentence-transformers/all-MiniLM-L6-v2", label: "all-MiniLM-L6-v2" }]

export default function ChatInterface() {
  const [settingsOpen, setSettingsOpen] = useState(true)
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "Hello! How can I help you today?" },
  ])
  const [inputValue, setInputValue] = useState("")
  const [darkMode, setDarkMode] = useState(true)
  const [fontSize, setFontSize] = useState(16)
  const [currentModel, setCurrentModel] = useState("gpt-4o-mini")
  const [apiKey, setApiKey] = useState("")
  const [showApiKey, setShowApiKey] = useState(false)
  const [embedderModelName, setEmbedderModelName] = useState("sentence-transformers/all-MiniLM-L6-v2")
  const [embeddingDim, setEmbeddingDim] = useState(384)
  const [topKChunks, setTopKChunks] = useState(10)
  const [topKRules, setTopKRules] = useState(3)
  const [topKSituations, setTopKSituations] = useState(2)
  const [threshold, setThreshold] = useState(0.6)
  const [situationThreshold, setSituationThreshold] = useState(0.8)
  const [temperature, setTemperature] = useState(0.0)
  const [maxLength, setMaxLength] = useState(4096)
  const [isLoading, setIsLoading] = useState(false)
  const [debugMode, setDebugMode] = useState(false)


  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    if (!darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }

  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}px`
  }, [fontSize])

  const buildRuleDebugInformation = (id: float, score: float, title: string, subrule_title) => {
    var information = "    - " + id + ": "
    information += title

    if(subrule_title) {
      information += " - " + subrule_title + " "
    }

    information += "(Score: " + score.toFixed(4) + ")"

    return information
  }

  const buildSituationDebugInformation = (situation_id: float, rule_id: float, score: float) => {
    var information = "    - Situation:" + situation_id + " - Rule: " + rule_id + " "
    information += "(Score: " + score.toFixed(4) + ")"

    return information
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    setMessages((prev) => [...prev, { role: "user", content: inputValue }])
    setInputValue("")
    setIsLoading(true)

    const settings = {
      model: currentModel,
      embedderModelName,
      embeddingDim,
      topKChunks,
      topKRules,
      topKSituations,
      threshold,
      situationThreshold,
      temperature,
      maxLength,
    }

    if (debugMode) {
      console.log("Debug: Sending message with settings", settings)
    }

    try {
      //const response = await fetch("https://89.58.11.37:8000/ask", {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "access_token": apiKey
        },
        body: JSON.stringify({
          gpt_model: currentModel,
          embedder_model_name: embedderModelName,
          embedding_dim: embeddingDim,
          top_k_chunks: topKChunks,
          top_k_rules: topKRules,
          top_k_situations: topKSituations,
          threshold: threshold,
          situation_threshold: situationThreshold,
          temperature: temperature,
          max_length: maxLength,
          question: inputValue
        }),
      })

      if (!response.ok) {
        const errorData = await response.json();
        console.log(errorData.detail);
        throw new Error(errorData.detail || "API request failed");
      }

      const data = await response.json()
      if (debugMode) {
        console.log("Debug: Received response", data)

        data.answer += "\n\n"
        data.answer += "----- Debug Information -----\n\n"

        data.answer += "All retrieved rules:\n"
        if(data.retrieved_all_rules.length > 0) {
          data.retrieved_all_rules.forEach((rule) => data.answer += buildRuleDebugInformation(rule.rule_id, rule.score_sum, rule.rule_title, rule.subrule_title) + "\n")
        } else {
          data.answer += "    - no rules retrieved\n"
        }

        data.answer += "\nAll retrieved top rules:\n"
        if(data.retrieved_top_rules.length > 0) {
          data.retrieved_top_rules.forEach((rule) => data.answer += buildRuleDebugInformation(rule.rule_id, rule.score_sum, rule.rule_title, rule.subrule_title) + "\n")
        } else {
          data.answer += "    - no top rules retrieved\n"
        }

        data.answer += "\nAll retrieved situations:\n"
        if(data.retrieved_situations.length > 0) {
          data.retrieved_situations.forEach((situation) => data.answer += buildSituationDebugInformation(situation.situation_id, situation.rule_id, situation.similarity) + "\n")
        } else {
          data.answer += "    - no situations retrieved\n"
        }
      }
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer }])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again.\n\n" + error },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const SliderWithInput = ({ label, value, onChange, min, max, step, tooltip }) => {
    const [localValue, setLocalValue] = useState(value)

    useEffect(() => {
      setLocalValue(value)
    }, [value])

    const handleSliderChange = (newValue: number[]) => {
      setLocalValue(newValue[0])
    }

    const handleSliderCommit = (newValue: number[]) => {
      onChange(newValue[0])
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value)
      if (newValue >= min && newValue <= max) {
        setLocalValue(newValue)
        onChange(newValue)
      }
    }

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-2 cursor-help">
                  <Label htmlFor={label}>{label}</Label>
                  <HelpCircle className="h-4 w-4" />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>{tooltip}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <Input
            type="number"
            value={localValue}
            onChange={handleInputChange}
            className="w-20 text-right"
            min={min}
            max={max}
            step={step}
          />
        </div>
        <Slider
          value={[localValue]}
          min={min}
          max={max}
          step={step}
          onValueChange={handleSliderChange}
          onValueCommit={handleSliderCommit}
        />
      </div>
    )
  }

  const IntegerInput = ({ label, value, onChange, min, max, tooltip, readOnly }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center gap-2 cursor-help">
                <Label htmlFor={label}>{label}</Label>
                <HelpCircle className="h-4 w-4" />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <Input
          type="number"
          value={value}
          onChange={(e) => onChange(Math.floor(Number(e.target.value)))}
          className="w-20 text-right"
          min={min}
          max={max}
          readOnly={readOnly}
        />
      </div>
    </div>
  )

  return (
    <div className={`flex h-screen bg-background text-foreground ${darkMode ? "dark" : ""}`}>
      {/* Settings Panel */}
      <div
        className={`h-full bg-muted border-r border-border transition-all duration-300 ${
          settingsOpen ? "w-80" : "w-0 overflow-hidden"
        }`}
      >
        <div className="p-4 h-full overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Settings</h2>
            <Button variant="ghost" size="icon" onClick={() => setSettingsOpen(false)}>
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </div>

          <Tabs defaultValue="model">
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="model">Model</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
            </TabsList>

            <TabsContent value="model" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="model-select">Model</Label>
                <Select value={currentModel} onValueChange={setCurrentModel}>
                  <SelectTrigger id="model-select">
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {GPT_MODELS.map((model) => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="api-key">OpenAI API Key</Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showApiKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your OpenAI API key"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              {/*
              <div className="space-y-2">
                <Label htmlFor="embedder-model-select">Embedder Model</Label>
                <Select value={embedderModelName} onValueChange={setEmbedderModelName}>
                  <SelectTrigger id="embedder-model-select">
                    <SelectValue placeholder="Select an embedder model" />
                  </SelectTrigger>
                  <SelectContent>
                    {EMBEDDER_MODELS.map((model) => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              

              <IntegerInput
                label="Embedding Dimension"
                value={embeddingDim}
                onChange={setEmbeddingDim}
                min={1}
                max={4096}
                tooltip="The dimension of the embedding vectors"
                readOnly="readOnly"
              />
              */}

              <IntegerInput
                label="Top K Chunks"
                value={topKChunks}
                onChange={setTopKChunks}
                min={1}
                max={100}
                tooltip="The number of top chunks to consider"
              />

              <IntegerInput
                label="Top K Rules"
                value={topKRules}
                onChange={setTopKRules}
                min={1}
                max={100}
                tooltip="The number of top rules to consider"
              />

              <IntegerInput
                label="Top K Situations"
                value={topKSituations}
                onChange={setTopKSituations}
                min={1}
                max={100}
                tooltip="The number of top situations to consider"
              />

              <SliderWithInput
                label="Threshold"
                value={threshold}
                onChange={setThreshold}
                min={0}
                max={1}
                step={0.01}
                tooltip="The similarity threshold for matching"
              />

              <SliderWithInput
                label="Situation Threshold"
                value={situationThreshold}
                onChange={setSituationThreshold}
                min={0}
                max={1}
                step={0.01}
                tooltip="The similarity threshold for situation matching"
              />

              <SliderWithInput
                label="Temperature"
                value={temperature}
                onChange={setTemperature}
                min={0}
                max={1}
                step={0.01}
                tooltip="Controls randomness in output generation"
              />

              <SliderWithInput
                label="Maximum Length"
                value={maxLength}
                onChange={setMaxLength}
                min={1}
                max={32768}
                step={1}
                tooltip="The maximum number of tokens in the generated response"
              />

              <div className="space-y-2">
                <h3 className="font-medium">Debug Mode</h3>
                <div className="flex items-center justify-between">
                  <span>Enable Debug Mode</span>
                  <Switch checked={debugMode} onCheckedChange={setDebugMode} />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="appearance" className="space-y-4">
              <div className="space-y-2">
                <h3 className="font-medium">Theme</h3>
                <div className="flex items-center justify-between">
                  <span>Dark Mode</span>
                  <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">Font Size</h3>
                <SliderWithInput
                  label="Font Size"
                  value={fontSize}
                  onChange={setFontSize}
                  min={12}
                  max={20}
                  step={1}
                  tooltip="Adjust the font size of the interface"
                />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 h-full overflow-hidden">
        {/* Header */}
        <header className="border-b border-border p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {!settingsOpen && (
              <Button variant="ghost" size="icon" onClick={() => setSettingsOpen(true)}>
                <Settings className="h-5 w-5" />
              </Button>
            )}
            <h1 className="text-xl font-semibold">Ice Hockey RuleBot</h1>
          </div>

          {/*
          <div className="flex items-center gap-2">
            <Select value={currentModel} onValueChange={setCurrentModel}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {GPT_MODELS.map((model) => (
                  <SelectItem key={model.value} value={model.value}>
                    {model.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          */}
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <Bot className="h-12 w-12 mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-semibold mb-2">How can I help you today?</h2>
              <p className="text-muted-foreground max-w-md">Ask me anything and I'll do my best to assist you.</p>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <Card
                    className={`max-w-3xl ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card text-card-foreground"}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex gap-3">
                      <Avatar
                        className={`flex items-center justify-center h-8 w-8 rounded-full border-2 border-black/20 ${
                          message.role === "assistant" ? "bg-white" : "bg-black"
                        }`}
                      >
                        {message.role === "assistant" ? (
                          <Bot className="h-4 w-4 text-black" />
                        ) : (
                          <User className="h-4 w-4 text-white" />
                        )}
                      </Avatar>
                        <div className="space-y-2">
                          <div className="font-medium">{message.role === "assistant" ? "RuleBot" : "You"}</div>
                          <div className="text-sm" style={{whiteSpace: "pre-wrap"}}>{message.content}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <Card className="max-w-3xl bg-card text-card-foreground">
                    <CardContent className="p-4">
                      <div className="flex gap-3 items-center">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src="/placeholder.svg?height=32&width=32" />
                          <AvatarFallback>
                            <Bot className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="space-y-2">
                          <div className="font-medium">RuleBot</div>
                          <div className="text-sm flex items-center">
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Thinking...
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-border p-4">
          <div className="max-w-3xl mx-auto relative">
            <Textarea
              placeholder="Message RuleBot..."
              className="pr-12 resize-none min-h-[60px] max-h-[200px] bg-background text-foreground"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <Button
              className="absolute right-2 bottom-2"
              size="icon"
              disabled={!inputValue.trim()}
              onClick={handleSendMessage}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <div className="text-xs text-center mt-2 text-muted-foreground">
            The Ice Hockey RuleBot <span style={{ textDecoration: 'line-through' }}>can</span> <b>will</b> make mistakes. Consider checking important information.
          </div>
        </div>
      </div>
    </div>
  )
}

