
import torch


def conv2d_output_shape(h, w, kernel_size=1, stride=1, padding=0, dilation=1):
    """
    Returns output H, W after convolution/pooling on input H, W.
    """
    kh, kw = kernel_size if isinstance(kernel_size, tuple) else (kernel_size,) * 2
    sh, sw = stride if isinstance(stride, tuple) else (stride,) * 2
    ph, pw = padding if isinstance(padding, tuple) else (padding,) * 2
    d = dilation
    h = (h + (2 * ph) - (d * (kh - 1)) - 1) // sh + 1
    w = (w + (2 * pw) - (d * (kw - 1)) - 1) // sw + 1
    return h, w


class ScaleGrad(torch.autograd.Function):

    @staticmethod
    def forward(ctx, tensor, scale):
        ctx.scale = scale
        return tensor

    @staticmethod
    def backward(ctx, grad_output):
        # We return as many input gradients as there were arguments.
        # Gradients of non-Tensor arguments to forward must be None.
        return grad_output * ctx.scale, None


scale_grad = ScaleGrad.apply


def update_state_dict(target_model, new_model, tau=1):
    if tau == 1:
        target_model.load_state_dict(new_model.state_dict())
    elif tau > 0:
        new_sd = new_model.state_dict()
        update_sd = {k: tau * new_sd[k] + (1 - tau) * v
            for k, v in target_model.state_dict().items()}
        target_model.load_state_dict(update_sd)
