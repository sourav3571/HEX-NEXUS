import { useMutation } from "@tanstack/react-query"
import api from "../../lib/axios/axios"
import { API_ROUTES } from "../../lib/api"
import { useRef, useState } from "react";
import { JsonViewer } from "../ui/home/JsonViewer";
import MessageBox from "../ui/home/MessageBox";

export default function Home() {

  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [operationHistory, setOperationHistory] = useState<{
    id: string;
    timestamp: number;
    type: 'analysis' | 'render';
    data: {
      knowYourKolam?: string;
      searchKolam?: string[];
      predictKolam?: string;
      renderedImage?: string;
    };
  }[]>([]);
  const [jsonInput, setJsonInput] = useState<string>("");


  const knowYourKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.KNOW_YOUR_KOLAM,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data;
    }
  });

  const searchKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.SEARCH,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data.matches;
    }
  });

  const predictKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(
        API_ROUTES.KOLAM.PREDICT,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return res.data.prediction;
    }
  });

  const renderKolamMuation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post(
        API_ROUTES.KOLAM.RENDER,
        data,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return res.data.file;
    },
    onSuccess: (data) => {
      setJsonInput("");
      setOperationHistory(prev => ([
        ...prev,
        {
          id: Date.now().toString(),
          timestamp: Date.now(),
          type: 'render',
          data: {
            renderedImage: data
          }
        }
      ]));
    }
  });

  const handleAnalyze = async () => {
    if (!file) return;

    try {
      const [knowResult, searchResult, predictResult] = await Promise.all([
        knowYourKolamMutation.mutateAsync(file),
        searchKolamMutation.mutateAsync(file),
        predictKolamMutation.mutateAsync(file)
      ]);

      // update unified history
      setOperationHistory(prev => ([
        ...prev,
        {
          id: Date.now().toString(),
          timestamp: Date.now(),
          type: 'analysis',
          data: {
            knowYourKolam: JSON.stringify(knowResult),
            searchKolam: searchResult,
            predictKolam: predictResult,
          }
        }
      ]));

      // clean up UI state
      setFile(null);
      setPreview(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (error) {
      console.error('Error analyzing kolam:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPreview(URL.createObjectURL(file));
      setFile(file);
    }
  };

  return (
    <div className="grid grid-cols-5 h-full w-full">
      {/* main content */}
      <div className="col-span-4 p-8 w-full bg-gray-50 h-screen overflow-y-auto">
        <div className="flex flex-col gap-8 h-full">
          {
            (!operationHistory || operationHistory.length < 1) && (
              <div className="w-full h-full bg-white rounded-2xl p-4 flex items-center justify-center flex-col">
                <img src="/logo.webp" alt="" />
                <p className="text-gray-500">Upload a kolam image to get started</p>
              </div>
            )
          }
          {
            operationHistory && operationHistory.length > 0 && operationHistory.map((operation) => {
              if (operation.type === 'analysis') {
                return (
                  <div key={operation.id} className="flex flex-col gap-6">
                    <MessageBox width="fit-content" text={`Hmm, I think it's from the ${operation.data.predictKolam}, it's well known as ${operation.data.predictKolam == "Maharastra" ? "Rangoli" : "Kolam"} in ${operation.data.predictKolam}.\nHere are some similar kolams I found in our database:`}>
                      <div className="grid grid-cols-3 gap-4">
                        {operation.data.searchKolam?.map((imgstr: string) => (
                          <div key={imgstr} className="h-[200px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                            <img
                              src={imgstr.startsWith('http') ? imgstr : `${import.meta.env.VITE_API_URL}/${imgstr}`}
                              alt="Similar kolam"
                              className="object-cover w-full h-full"
                            />
                          </div>
                        ))}
                      </div>
                    </MessageBox>
                    <MessageBox width="fit-content" text={`Here's a Mathematical representation of your kolam (in JSON format) \nYou can copy and generate using our kolam renderer API`}>
                      <JsonViewer text={operation.data.knowYourKolam || ""} />
                    </MessageBox>
                  </div>
                );
              } else if (operation.type === 'render') {
                return (
                  <MessageBox key={operation.id} width="fit-content" text={`Here's the kolam rendered from your JSON input`}>
                    <div className="h-[300px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                      <object
                        type="image/svg+xml"
                        data={operation.data.renderedImage?.startsWith("http") ? operation.data.renderedImage : `${import.meta.env.VITE_API_URL}/${operation.data.renderedImage}`}
                        className="w-full h-full"
                      />
                    </div>
                  </MessageBox>
                );
              }
              return null;
            })
          }
          <div className="pt-8"></div>
        </div>
      </div>
      {/* sidebar */}
      <div className="col-span-1 border-l border-gray-200 p-5">
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        <div
          className="w-full aspect-square flex flex-col items-center justify-center border-2 border-dashed border-gray-400 rounded-2xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition overflow-hidden"
          onClick={() => inputRef.current?.click()}
        >
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="object-cover w-full h-full"
            />
          ) : (
            <>
              <span className="text-4xl text-gray-500">+</span>
              <p className="text-gray-600 mt-2">Upload Photo</p>
            </>
          )}
        </div>
        {
          file ? (
            <button
              className="px-4 py-2 text-primary border-1 font-semibold border-primary rounded-lg mt-4 bg-white"
              onClick={handleAnalyze}
              disabled={knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending}
            >
              {(knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending) ? "Analyzing kolam..." : "Analyze"}
            </button>
          ) : null
        }
        <textarea
          className="w-full border border-gray-300 rounded-lg p-4 mt-8 resize-none text-xs"
          placeholder="Add json to render kolam.."
          rows={10}
          onChange={(e) => setJsonInput(e.target.value)}
          value={jsonInput}
        ></textarea>

        {jsonInput.trim().length > 0 ? (
          <button
            className="px-4 py-2 text-primary border-1 font-semibold border-primary rounded-lg mt-4 bg-white"
            onClick={() => {
              try {
                const parsed = JSON.parse(jsonInput); // must be object with dots + paths
                renderKolamMuation.mutate(parsed);
              } catch {
                alert("Invalid JSON");
              }
            }}
            disabled={renderKolamMuation.isPending}
          >
            Render Kolam
          </button>
        ) : null}
      </div>
    </div>
  )
}