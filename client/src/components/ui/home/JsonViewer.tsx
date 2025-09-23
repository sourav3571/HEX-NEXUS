import React from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { coy } from "react-syntax-highlighter/dist/esm/styles/prism";

type JsonViewerProps = {
  text: string;
};

export const JsonViewer: React.FC<JsonViewerProps> = ({ text }) => {
  let prettyJson = "";
  try {
    prettyJson = JSON.stringify(JSON.parse(text), null, 2);
  } catch (e) {
    prettyJson = "Invalid JSON";
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(prettyJson);
    } catch (err) {
      console.error("Failed to copy JSON", err);
    }
  };

  return (
    <div className="relative w-full">
      {/* Copy Button */}
      <button
        onClick={copyToClipboard}
        className="z-10 absolute top-2 right-2 px-2 py-1 bg-gray-200 hover:bg-gray-200 rounded text-xs text-gray-500"
      >
        Copy
      </button>

      {/* Syntax highlighted JSON */}
      <SyntaxHighlighter
        language="json"
        style={coy}
        customStyle={{
          margin: 0,
          background: "transparent",
          fontSize: "12px",
          maxHeight: "400px",
          minWidth: "300px",
          backgroundColor: "#f9f9f9",
          borderRadius: "8px",
          padding: "16px",
          overflow: "hidden"
        }}
      >
        {prettyJson}
      </SyntaxHighlighter>
    </div>
  );
};
