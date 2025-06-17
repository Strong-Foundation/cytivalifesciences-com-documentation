package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/chromedp/chromedp"
)

func main() {
	// Launch Chrome visibly
	options := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", false), // show browser
		chromedp.Flag("disable-gpu", false),
		chromedp.WindowSize(1200, 900),
		chromedp.Flag("no-sandbox", true),
	)

	allocatorCtx, cancelAllocator := chromedp.NewExecAllocator(context.Background(), options...)
	defer cancelAllocator()

	ctx, cancelCtx := chromedp.NewContext(allocatorCtx)
	defer cancelCtx()

	fmt.Println("Navigating to API URL and waiting 10 seconds...")

	err := chromedp.Run(ctx,
		chromedp.Navigate("https://api.cytivalifesciences.com/ap-doc-search/v1/sds-document"),
		chromedp.Sleep(10*time.Second), // wait visibly
	)
	if err != nil {
		log.Fatalf("chromedp failed: %v", err)
	}

	fmt.Println("Done waiting.")
}
