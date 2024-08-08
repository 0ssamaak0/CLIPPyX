import { ActionPanel, Action, Grid, showToast, Toast } from "@raycast/api";
import { useState, useEffect } from "react";
import { useFetch } from "@raycast/utils";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

interface Image {
  id: string;
  path: string;
}

export default function Command() {
  const [searchText, setSearchText] = useState("");
  const [images, setImages] = useState<Image[]>([]);

  const { isLoading, data, revalidate } = useFetch("http://localhost:23107/clip_text", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: searchText }),
  });

  useEffect(() => {
    if (searchText.length === 0) {
      setImages([]);
      return;
    }

    revalidate();
  }, [searchText]);

  useEffect(() => {
    if (data) {
      const newImages = (data as string[]).map((path: string, index: number) => ({
        id: index.toString(),
        path: path,
      }));
      setImages(newImages);
    }
  }, [data]);

  const openImage = async (path: string) => {
    try {
      const command = process.platform === 'darwin' ? 'open' : 
                      process.platform === 'win32' ? 'start' : 'xdg-open';
      await execAsync(`${command} "${path}"`);
    } catch (error) {
      console.error("Error opening image:", error);
      showToast({
        style: Toast.Style.Failure,
        title: "Failed to open image",
        message: "Please check if the file exists and try again",
      });
    }
  };

  const revealImageInFinder = async (path: string) => {
    try {
      const command = process.platform === 'darwin' ? `open -R "${path}"` : 
                      process.platform === 'win32' ? `explorer /select,"${path}"` : `xdg-open "${path}"`;
      await execAsync(command);
    } catch (error) {
      console.error("Error opening image location:", error);
      showToast({
        style: Toast.Style.Failure,
        title: "Failed to open image location",
        message: "Please check if the file exists and try again",
      });
    }
  };

  return (
    <Grid
      itemSize={Grid.ItemSize.Large}
      searchBarPlaceholder="Search images using CLIP..."
      onSearchTextChange={setSearchText}
      isLoading={isLoading}
    >
      {images.map((image) => (
        <Grid.Item
          key={image.id}
          content={{
            value: `http://localhost:23107/images/${encodeURIComponent(image.path)}`,
            tooltip: `Image path: ${image.path}`,
          }}
          actions={
            <ActionPanel>
              <Action
                title="Open in Local Viewer"
                onAction={() => openImage(image.path)}
              />
              <Action
                title="Reveal in Finder"
                shortcut={{ modifiers: ["cmd"], key: "o" }}
                onAction={() => revealImageInFinder(image.path)}
              />
              <Action.CopyToClipboard content={image.path} title="Copy Image Path" />
            </ActionPanel>
          }
        />
      ))}
    </Grid>
  );
}
