package exp.engine.dsl.ide;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.nio.channels.Channels;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.Function;

import org.eclipse.lsp4j.jsonrpc.Launcher;
import org.eclipse.lsp4j.jsonrpc.MessageConsumer;
import org.eclipse.lsp4j.services.LanguageClient;
import org.eclipse.xtext.ide.server.LanguageServerImpl;
import org.eclipse.xtext.ide.server.ServerModule;

import com.google.inject.Guice;
import com.google.inject.Injector;

public class RunServer {

    public static void main(String[] args) throws InterruptedException, IOException {
        System.out.println("Welcome to Experiment LSP version 4.0 - Resolved");
        Injector injector = Guice.createInjector(new ServerModule());
        LanguageServerImpl languageServer = injector.getInstance(LanguageServerImpl.class);
        Function<MessageConsumer, MessageConsumer> wrapper = consumer -> consumer;

        AsynchronousServerSocketChannel serverSocket = AsynchronousServerSocketChannel.open().bind(new InetSocketAddress("0.0.0.0", 5007));
        ExecutorService executorService = Executors.newCachedThreadPool();

        while (true) {
            try {
                AsynchronousSocketChannel socketChannel = serverSocket.accept().get();
                handleClientConnection(languageServer, socketChannel, executorService, wrapper);
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }
    }

    private static void handleClientConnection(LanguageServerImpl languageServer, AsynchronousSocketChannel socketChannel, ExecutorService executorService, Function<MessageConsumer, MessageConsumer> wrapper) {
        executorService.submit(() -> {
            try {
                Launcher<LanguageClient> launcher = Launcher.createIoLauncher(
                        languageServer, 
                        LanguageClient.class,
                        Channels.newInputStream(socketChannel),
                        Channels.newOutputStream(socketChannel),
                        executorService,
                        wrapper);
                languageServer.connect(launcher.getRemoteProxy());
                Future<?> future = launcher.startListening();
                future.get();
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        });
    }
}